"""
Pipeline Monitor - Checks the health of the data pipeline
Shows last update time, data freshness, error logs, and system status
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.models.database import Market, Database


class PipelineMonitor:
    """Monitors the health and status of the data pipeline"""
    
    def __init__(self):
        self.db = Database()
        self.log_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'logs',
            'data_pipeline.log'
        )
    
    def get_last_update_time(self):
        """Get the timestamp of the most recently updated market"""
        session = self.db.get_session()
        try:
            latest_market = session.query(Market).order_by(
                Market.updated_at.desc()
            ).first()
            
            if latest_market:
                return latest_market.updated_at
            return None
        finally:
            session.close()
    
    def get_data_freshness(self):
        """Calculate how old the most recent data is"""
        last_update = self.get_last_update_time()
        
        if not last_update:
            return None, "No data in database"
        
        age = datetime.utcnow() - last_update
        
        if age < timedelta(minutes=20):
            status = "✓ FRESH"
        elif age < timedelta(hours=1):
            status = "⚠ STALE"
        else:
            status = "✗ VERY STALE"
        
        return age, status
    
    def get_market_stats(self):
        """Get statistics about markets in the database"""
        session = self.db.get_session()
        try:
            total_markets = session.query(Market).count()
            active_markets = session.query(Market).filter_by(active=True).count()
            resolved_markets = session.query(Market).filter_by(resolved=True).count()
            crypto_markets = session.query(Market).count()  # All are crypto filtered
            
            return {
                'total': total_markets,
                'active': active_markets,
                'resolved': resolved_markets,
                'crypto': crypto_markets
            }
        finally:
            session.close()
    
    def get_recent_errors(self, lines=10):
        """Get recent error messages from the pipeline log"""
        if not os.path.exists(self.log_file):
            return []
        
        errors = []
        try:
            with open(self.log_file, 'r') as f:
                for line in f.readlines()[-100:]:  # Check last 100 lines
                    if 'ERROR' in line or 'WARNING' in line:
                        errors.append(line.strip())
        except Exception as e:
            return [f"Error reading log file: {str(e)}"]
        
        return errors[-lines:]  # Return last 10 errors
    
    def get_log_summary(self):
        """Get summary of pipeline operations from log"""
        if not os.path.exists(self.log_file):
            return {
                'total_fetches': 0,
                'successful_fetches': 0,
                'failed_fetches': 0
            }
        
        successful = 0
        failed = 0
        
        try:
            with open(self.log_file, 'r') as f:
                for line in f:
                    if 'Data fetch completed successfully' in line:
                        successful += 1
                    elif 'Fatal error in fetch_and_store_markets' in line:
                        failed += 1
        except Exception as e:
            return {'error': f"Could not read log: {str(e)}"}
        
        return {
            'total_fetches': successful + failed,
            'successful_fetches': successful,
            'failed_fetches': failed,
            'success_rate': f"{(successful / (successful + failed) * 100):.1f}%" if (successful + failed) > 0 else "N/A"
        }
    
    def print_status(self):
        """Print comprehensive pipeline status"""
        print("\n" + "=" * 70)
        print(" " * 20 + "DATA PIPELINE MONITOR")
        print("=" * 70)
        
        # Last Update
        print("\n📊 DATA FRESHNESS:")
        last_update = self.get_last_update_time()
        if last_update:
            print(f"   Last Update: {last_update.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            age, status = self.get_data_freshness()
            print(f"   Data Age: {status}")
            print(f"   Duration: {age}")
        else:
            print("   No data updates yet")
        
        # Market Statistics
        print("\n📈 MARKET STATISTICS:")
        stats = self.get_market_stats()
        print(f"   Total Markets: {stats['total']}")
        print(f"   Active Markets: {stats['active']}")
        print(f"   Resolved Markets: {stats['resolved']}")
        print(f"   Crypto Markets: {stats['crypto']}")
        
        # Pipeline Performance
        print("\n⚙️  PIPELINE PERFORMANCE:")
        log_summary = self.get_log_summary()
        if 'error' not in log_summary:
            print(f"   Total Fetches: {log_summary['total_fetches']}")
            print(f"   Successful: {log_summary['successful_fetches']}")
            print(f"   Failed: {log_summary['failed_fetches']}")
            print(f"   Success Rate: {log_summary['success_rate']}")
        else:
            print(f"   {log_summary['error']}")
        
        # Recent Errors
        print("\n⚠️  RECENT ERRORS & WARNINGS:")
        errors = self.get_recent_errors(5)
        if errors:
            for error in errors:
                print(f"   {error}")
        else:
            print("   No errors or warnings")
        
        # System Status
        print("\n✅ SYSTEM STATUS:")
        if last_update and datetime.utcnow() - last_update < timedelta(minutes=20):
            print("   Pipeline: ✓ RUNNING NORMALLY")
        elif last_update and datetime.utcnow() - last_update < timedelta(hours=1):
            print("   Pipeline: ⚠ RUNNING BUT DATA IS STALE")
        else:
            print("   Pipeline: ✗ NOT UPDATING")
        
        print("\n" + "=" * 70)
        print(f"Monitor Report Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print("=" * 70 + "\n")
    
    def export_status_json(self, filepath=None):
        """Export status as JSON for programmatic access"""
        if filepath is None:
            log_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            filepath = os.path.join(log_dir, 'logs', 'pipeline_status.json')
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        last_update = self.get_last_update_time()
        age, status = self.get_data_freshness()
        
        status_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'last_update': last_update.isoformat() if last_update else None,
            'data_freshness': {
                'age_minutes': age.total_seconds() / 60 if age else None,
                'status': status
            },
            'market_stats': self.get_market_stats(),
            'pipeline_performance': self.get_log_summary()
        }
        
        try:
            with open(filepath, 'w') as f:
                json.dump(status_data, f, indent=2)
            print(f"✓ Status exported to {filepath}")
        except Exception as e:
            print(f"✗ Error exporting status: {str(e)}")


def main():
    """Run the monitor and display results"""
    monitor = PipelineMonitor()
    
    # Print current status
    monitor.print_status()
    
    # Export as JSON for programmatic access
    monitor.export_status_json()


if __name__ == "__main__":
    main()
