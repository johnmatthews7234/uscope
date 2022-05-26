from .models import JobList, JobResults, Place, PlaceGoogle

class rawreport:
    def __init__(self, job_number):
        self.job_number = job_number
        self.job_record = JobList.query.filter(JobList.id == self.job_number).first()
        self.job_results = JobResults.query.filter(JobResults.joblistid == self.job_number).all()

    def create_report(self):
        output = []
        for place in self.job_results:
            place_record = Place.query.filter(Place.id == place.id).first()
            if place_record is None: continue
            place_record = place_record.__dict__
            place_google_record = PlaceGoogle.query.filter(PlaceGoogle.placeid == place.id).first()
            if place_google_record is None: place_google_record = PlaceGoogle()
            place_record = {**place_google_record.__dict__, **place_record }
            del place_record['_sa_instance_state']
            output.append(place_record)
        return output