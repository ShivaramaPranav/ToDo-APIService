import sys
sys.path.append("..")

from db import db

class PlayerMatch(db.Model):
    __tablename__ = 'playermatch'
    
    id = db.Column(db.Integer, primary_key=True)
    matchId = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    playerId = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    earnedPoints = db.Column(db.Integer, nullable=False)
    
    def __init__(self, matchId, playerId, earnedPoints):
        self.matchId = matchId
        self.playerId = playerId
        self.earnedPoints = earnedPoints
    
    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def find_by_player(cls, playerId):
        return cls.query.filter_by(playerId=playerId).all()

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
            "playerId": self.winner,
            "matchId": self.loser,
            "earnedPoints": self.earnedPoints
        }