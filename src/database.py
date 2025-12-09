"""Database models and operations for summary history."""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict


class SummaryDatabase:
    """Manages summary history in SQLite database."""
    
    def __init__(self, db_path: str = "summaries.db"):
        """Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Create database tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_text TEXT NOT NULL,
                summary_text TEXT NOT NULL,
                summary_style TEXT NOT NULL,
                original_length INTEGER NOT NULL,
                summary_length INTEGER NOT NULL,
                compression_rate REAL NOT NULL,
                model_used TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_summary(
        self,
        original_text: str,
        summary_text: str,
        summary_style: str,
        original_length: int,
        summary_length: int,
        compression_rate: float,
        model_used: str,
        metadata: Optional[Dict] = None
    ) -> int:
        """Save a summary to the database.
        
        Args:
            original_text: Original content
            summary_text: Generated summary
            summary_style: Style used for summary
            original_length: Length of original text
            summary_length: Length of summary
            compression_rate: Compression percentage
            model_used: AI model used
            metadata: Additional metadata
            
        Returns:
            ID of the saved summary
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        metadata_json = json.dumps(metadata) if metadata else None
        
        cursor.execute("""
            INSERT INTO summaries (
                original_text, summary_text, summary_style,
                original_length, summary_length, compression_rate,
                model_used, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            original_text, summary_text, summary_style,
            original_length, summary_length, compression_rate,
            model_used, metadata_json
        ))
        
        summary_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return summary_id
    
    def get_summary(self, summary_id: int) -> Optional[Dict]:
        """Get a specific summary by ID.
        
        Args:
            summary_id: ID of the summary
            
        Returns:
            Dictionary with summary data or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM summaries WHERE id = ?
        """, (summary_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_all_summaries(
        self,
        limit: int = 100,
        offset: int = 0,
        style_filter: Optional[str] = None
    ) -> List[Dict]:
        """Get all summaries with optional filtering.
        
        Args:
            limit: Maximum number of results
            offset: Number of results to skip
            style_filter: Filter by summary style
            
        Returns:
            List of summary dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if style_filter:
            cursor.execute("""
                SELECT * FROM summaries
                WHERE summary_style = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (style_filter, limit, offset))
        else:
            cursor.execute("""
                SELECT * FROM summaries
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def delete_summary(self, summary_id: int) -> bool:
        """Delete a summary by ID.
        
        Args:
            summary_id: ID of the summary to delete
            
        Returns:
            True if deleted, False if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM summaries WHERE id = ?", (summary_id,))
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return deleted
    
    def get_statistics(self) -> Dict:
        """Get summary statistics.
        
        Returns:
            Dictionary with statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total summaries
        cursor.execute("SELECT COUNT(*) FROM summaries")
        total_summaries = cursor.fetchone()[0]
        
        # Average compression rate
        cursor.execute("SELECT AVG(compression_rate) FROM summaries")
        avg_compression = cursor.fetchone()[0] or 0
        
        # Summaries by style
        cursor.execute("""
            SELECT summary_style, COUNT(*) as count
            FROM summaries
            GROUP BY summary_style
        """)
        by_style = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Recent activity (last 7 days)
        cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM summaries
            WHERE created_at >= datetime('now', '-7 days')
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        """)
        recent_activity = [
            {"date": row[0], "count": row[1]}
            for row in cursor.fetchall()
        ]
        
        conn.close()
        
        return {
            "total_summaries": total_summaries,
            "average_compression": round(avg_compression, 1),
            "by_style": by_style,
            "recent_activity": recent_activity
        }
    
    def search_summaries(self, query: str, limit: int = 50) -> List[Dict]:
        """Search summaries by text content.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching summaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        search_pattern = f"%{query}%"
        cursor.execute("""
            SELECT * FROM summaries
            WHERE original_text LIKE ? OR summary_text LIKE ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (search_pattern, search_pattern, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
