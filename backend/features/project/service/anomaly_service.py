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
        # Target Parent Status
        target_parent_statuses = ["Open"] 
        
        # Child "Active" Statuses
        active_child_statuses = [
            "In Progress", "Development", "Testing", 
            "In Review", "Review", 
            "Resolved", 
            "Done", "Closed"
        ]

        # Query Potential Anomalous Parents
        # Must belong to this TP, be one of the types, and be Open.
        parents = self.db.query(LarkModelTCG).filter(
            LarkModelTCG.tp_number == tp.ticket_number,
            LarkModelTCG.issue_type.in_(target_issue_types),
            LarkModelTCG.jira_status.in_(target_parent_statuses)
        ).all()

        for p in parents:
            # check children
            # Optimization: could be better, but N+1 safe for background job
            children = self.db.query(LarkModelTCG).filter(
                LarkModelTCG.parent_tickets.ilike(f"%{p.tcg_tickets}%")
            ).all()

            if not children:
                continue

            has_active_child = False
            active_child_info = []

            for c in children:
                c_status = (c.jira_status or "").strip()
                # Check fuzzy match or exact match depending on data cleanliness
                # Here we check exact match against the list
                if c_status in active_child_statuses:
                    has_active_child = True
                    active_child_info.append(f"{c.tcg_tickets}({c_status})")
                    break # As per requirement "Any child"

            if has_active_child:
                # Found Anomaly
                reason = f"Parent is Open but has active child: {', '.join(active_child_info)}"
                anomaly = TicketAnomaly(
                    ticket_number=p.tcg_tickets,
                    ticket_title=p.title,
                    tp_number=p.tp_number,
                    tp_title=tp.title,
                    assignee=p.assignee,
                    parent_status=p.jira_status,
                    anomaly_reason=reason,
                    detected_at=timestamp
                )
                self.db.add(anomaly)
