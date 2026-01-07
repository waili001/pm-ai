from sqlalchemy.orm import Session
from sqlalchemy import func, and_, not_, or_
from backend.features.project.persistence.models import LarkModelTP
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ProjectService:
    def __init__(self, db: Session):
        self.db = db

    def _get_quarter(self, date_obj):
        if not date_obj:
            return None
        return f"{date_obj.year} Q{(date_obj.month - 1) // 3 + 1}"

    def _parse_date(self, val):
        if not val:
            return None
        try:
            # Try timestamp (ms)
            if str(val).isdigit() and len(str(val)) > 10:
                return datetime.fromtimestamp(int(val) / 1000)
            # Try timestamp (s)
            if str(val).isdigit():
                return datetime.fromtimestamp(int(val))
            # Try ISO format or similar "YYYY-MM-DD"
            return datetime.strptime(str(val).split('T')[0], "%Y-%m-%d")
        except Exception as e:
            return None

    def get_dashboard_stats(self, department: str = None):
        """
        Calculate statistics for the dashboard.
        Metric: Closed TP Count by Quarter (Last 4 Quarters)
        """
        query = self.db.query(LarkModelTP).filter(
            LarkModelTP.jira_status.in_(["Closed", "Resolved"])
        )
        
        if department and department != "ALL":
             query = query.filter(LarkModelTP.department.ilike(f"%{department}%"))
        else:
             # Exclude if Department is WRD AND (Title starts with "WLB_" OR Project Type is empty)
             query = query.filter(
                 not_(
                     and_(
                         LarkModelTP.department == "WRD",
                         or_(
                             LarkModelTP.title.like("WLB_%"),
                             LarkModelTP.project_type.is_(None),
                             LarkModelTP.project_type == "",
                             LarkModelTP.project_type == "Others"
                         )
                     )
                 )
             )
        
        tps = query.all()
        
        # Determine Date Range (Last 4 Quarters approx 1 year)
        now = datetime.now()
        
        # Generate target quarters list (Current + Previous 3)
        target_quarters = []
        curr = now
        for _ in range(4):
            q_str = self._get_quarter(curr)
            target_quarters.append(q_str)
            curr = curr - timedelta(days=95)
        
        target_quarters.reverse() # Ascending order
        stats = {q: 0 for q in target_quarters}
        icr_stats = {q: 0 for q in target_quarters}

        for tp in tps:
            d_obj = self._parse_date(tp.released_date)
            if d_obj:
                q_str = self._get_quarter(d_obj)
                if q_str in stats:
                    stats[q_str] += 1
                    
                    # Logic for ICR Count Chart
                    # "display the total sum of the icr_count of TPs where TP project type is ICR"
                    if tp.project_type == "ICR":
                         icr_count = tp.icr_count or 0 # Handle None
                         icr_stats[q_str] += icr_count
        
        return {
            "categories": list(stats.keys()),
            "data": list(stats.values()),
            "icr_data": list(icr_stats.values())
        }

    def get_closed_tps(self, quarter: str, department: str = None):
        """
        Get list of Closed/Resolved TPs for a specific quarter.
        """
        query = self.db.query(LarkModelTP).filter(
            LarkModelTP.jira_status.in_(["Closed", "Resolved"])
        )

        if department and department != "ALL":
             query = query.filter(LarkModelTP.department.ilike(f"%{department}%"))
        else:
             # Exclude if Department is WRD AND (Title starts with "WLB_" OR Project Type is empty)
             query = query.filter(
                 not_(
                     and_(
                         LarkModelTP.department == "WRD",
                         or_(
                             LarkModelTP.title.like("WLB_%"),
                             LarkModelTP.project_type.is_(None),
                             LarkModelTP.project_type == "",
                             LarkModelTP.project_type == "Others"
                         )
                     )
                 )
             )

        tps = query.all()
        results = []

        for tp in tps:
            d_obj = self._parse_date(tp.released_date)
            if d_obj:
                q_str = self._get_quarter(d_obj)
                if q_str == quarter:
                    # Match found
                    results.append({
                        "id": tp.record_id,
                        "ticket_number": tp.ticket_number,
                        "title": tp.title,
                        "project_type": tp.project_type,
                        "department": tp.department,
                        "released_date": d_obj.strftime('%Y-%m-%d'), # Normalized date
                        "project_manager": tp.project_manager
                    })
        
        return results
