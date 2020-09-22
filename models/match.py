import sys
sys.path.append("..")

from db import db

class Match(db.Model):
    __tablename__ = 'match'
    
    id = db.Column(db.Integer, primary_key=True)
    winner = db.Column(db.String(10), nullable=False)
    loser = db.Column(db.String(10), nullable=False)
    
    def __init__(self, winner, loser):
        self.winner = winner
        self.loser = loser
    
    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def find_by_winner(cls, winner):
        return cls.query.filter_by(winner=winner).first()

    @classmethod
    def find_all(cls):
        return cls.query.all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
    
    def json(self):
        return {
            "id": self.id,
            "winner": self.winner,
            "loser": self.loser
        }