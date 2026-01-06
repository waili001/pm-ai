import time
from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..persistence.models import LarkModelTCG, LarkModelTP, TicketAnomaly

class AnomalyService:
    def __init__(self, db: Session):
        self.db = db

    def refresh_anomalies(self):
        """
        Scans for anomalies in 'In Progress' TPs and updates the ticket_anomalies table.
        Rule: Parent is Open, but Child is In Progress/Done.
        """
        # 1. Get In Progress TPs
        active_tps = self.db.query(LarkModelTP).filter(
            LarkModelTP.jira_status == "In Progress"
        ).all()
        
        tp_numbers = [tp.ticket_number for tp in active_tps]
        if not tp_numbers:
            return

        current_time = int(time.time() * 1000)
        
        # Clear existing anomalies for these TPs to avoid duplicates/stale data
        self.db.query(TicketAnomaly).filter(
            TicketAnomaly.tp_number.in_(tp_numbers)
        ).delete(synchronize_session=False)

        # 2. Iterate TPs and find anomalies
        for tp in active_tps:
            self._detect_anomalies_for_tp(tp, current_time)
        
        self.db.commit()

    def _detect_anomalies_for_tp(self, tp: LarkModelTP, timestamp: int):
        # Target Parent Issue Types
        target_issue_types = ["Change Request", "Improvement"]
        # Rule 1 Active Children Statuses (Open Parent)
        active_child_statuses = [
            "In Progress", "Development", "Testing", 
            "In Review", "Review", 
            "Resolved", 
            "Done", "Closed"
        ]
        
        # Rule 2 Inactive Children Statuses (In Progress Parent) -> Check if ALL are in this list
        inactive_child_statuses = ["Resolved", "Done", "Closed"]

        # Query Potential Parents (Open OR In Progress)
        target_statuses = ["Open", "In Progress"]
        
        parents = self.db.query(LarkModelTCG).filter(
            LarkModelTCG.tp_number == tp.ticket_number,
            LarkModelTCG.issue_type.in_(target_issue_types),
            LarkModelTCG.jira_status.in_(target_statuses)
        ).all()

        for p in parents:
            # check children
            children = self.db.query(LarkModelTCG).filter(
                LarkModelTCG.parent_tickets.ilike(f"%{p.tcg_tickets}%")
            ).all()

            if not children:
                continue

            c_statuses = [(c.jira_status or "").strip() for c in children]
            parent_status = (p.jira_status or "").strip()

            # --- Rule 1: Parent Open but Child Active ---
            if parent_status == "Open":
                has_active_child = False
                active_child_info = []
                for c in children:
                    c_status = (c.jira_status or "").strip()
                    if c_status in active_child_statuses:
                        has_active_child = True
                        active_child_info.append(f"{c.tcg_tickets}({c_status})")
                
                if has_active_child:
                    reason = f"Parent is Open but has active child: {', '.join(active_child_info)}"
                    self._create_anomaly(p, tp, reason, timestamp)

            # --- Rule 2: Parent In Progress but Child InActive ---
            elif parent_status == "In Progress":
                # Check if ALL children are inactive
                all_inactive = True
                for c_status in c_statuses:
                    if c_status not in inactive_child_statuses:
                        all_inactive = False
                        break
                
                if all_inactive:
                    reason = "Parent is In Progress but all children are InActive (Closed/Done)."
                    self._create_anomaly(p, tp, reason, timestamp)

    def _create_anomaly(self, p, tp, reason, timestamp):
        anomaly = TicketAnomaly(
            ticket_number=p.tcg_tickets,
            ticket_title=p.title,
            tp_number=p.tp_number,
            tp_title=tp.title,
            assignee=p.assignee,
            parent_status=p.jira_status,
            anomaly_reason=reason,
            detected_at=timestamp,
            components=p.components,
            department=p.department
        )
        self.db.add(anomaly)
