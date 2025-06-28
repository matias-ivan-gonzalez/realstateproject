from database import db
from datetime import datetime

class MensajeChat(db.Model):
    __tablename__ = 'mensajes_chat'
    id = db.Column(db.Integer, primary_key=True)
    conversacion_id = db.Column(db.Integer, db.ForeignKey('conversaciones.id'), nullable=False)
    user = db.Column(db.String(100), nullable=False)
    rol = db.Column(db.String(50), nullable=False)
    msg = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'user': self.user,
            'rol': self.rol,
            'msg': self.msg,
            'conversacion_id': self.conversacion_id,
            'timestamp': self.timestamp.isoformat()
        }
