import sys
sys.path.append("..")

from db import db

class Player(db.Model):
    __tablename__ = 'player'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    csk = db.Column(db.Integer, nullable=False)
    dc = db.Column(db.Integer, nullable=False)
    kxip = db.Column(db.Integer, nullable=False)
    kkr = db.Column(db.Integer, nullable=False)
    mi = db.Column(db.Integer, nullable=False)
    rr = db.Column(db.Integer, nullable=False)
    rcb = db.Column(db.Integer, nullable=False)
    srh = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer, nullable=False)

    
    def __init__(self, name,  csk, dc, kxip, kkr, mi, rr, rcb, srh, score=0):
        self.name = name
        self.csk = csk
        self.dc = dc
        self.kxip = kxip
        self.kkr = kkr
        self.mi = mi
        self.rr = rr
        self.rcb = rcb
        self.srh = srh
        self.score = score
    
    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

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
            "name": self.name,
            "csk": self.csk,
            "dc": self.dc,
            "kxip": self.kxip,
            "kkr": self.kkr,
            "mi": self.mi,
            "rr": self.rr,
            "rcb": self.rcb,
            "srh": self.srh,
            "score": self.score
        }