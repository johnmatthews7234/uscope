import threading
import io
from flask import Blueprint, flash, redirect, render_template, request, send_file
from werkzeug.exceptions import abort
from json_excel_converter import Converter
from json_excel_converter.xlsx import Writer
from .models import JobList, JobResults, Place, PlaceGoogle
from .db import db_session
from .googlescrape import street_address_to_lat_lng, google_search
from .reports import rawreport


bp = Blueprint('gsearch', __name__, url_prefix='/gsearch')

@bp.route('/', methods=('GET', 'POST',))
def gsearch():
    if request.method == 'POST':
        error = None
        job_dict = {}
        address = request.form['address']
        if not address:
            error = 'An address is required.'
        radius = request.form['radius']
        if not radius:
            error = 'A radius is required.'
        keyword = request.form['keyword']
        if not keyword:
            error = 'A keyword is required'
        job_dict['address'] = address
        job_dict['radius'] = radius
        job_dict['placelist'] = []
        filter = request.form.get('filter') == True
        job_dict['count'] = 0
        my_job = JobList(pointaddress=address, radius=radius, placecount=0, searchterms=keyword)
        db_session.add(my_job)
        db_session.commit()
        job_id = my_job.id
        try:
            lat_lng = street_address_to_lat_lng(address)
        except Exception as e:
            error = str(e)
            flash(error)
            return render_template('/gsearch/search.html')
        job_dict['lat'] = lat_lng['lat']
        job_dict['lng'] = lat_lng['lng']
        my_job.lat = lat_lng['lat']
        my_job.lng = lat_lng['lng']
        try:
            my_google_search = google_search(address, radius,keyword)
            google_place_list = my_google_search.get_google_id_list()
            google_thread = threading.Thread(target=my_google_search.get_place_id_list, kwargs={'job_number': job_id, 'filter' : filter})
            google_thread.start()
            job_dict['count'] = len(google_place_list)
            my_job.placecount = len(google_place_list)
        except Exception as e:
            error = str(e)
        my_job.complete = False
        db_session.commit()
        if error is None:
            return redirect('/gsearch/jobdisplay/' + str (job_id))
        flash(error)
    return render_template('/gsearch/gsearch.html')

@bp.route('/jobdisplay/<int:job_number>', methods=('GET',))
def job_display(job_number):
    return render_template('/gsearch/jobdisplay.html', record=get_job_details(job_number), placelist=get_job_place_list(job_number))

def get_job_details(job_number):
    my_job_details = JobList.query.filter(JobList.id == job_number).first().__dict__
    if my_job_details is not None:
        return my_job_details
    else:
        raise Exception(f"Job {job_number} does not exist.")
    
def get_job_place_list(job_number):
    my_job_records = JobResults.query.filter(JobResults.joblistid == job_number).all()
    if my_job_records is None:
        raise Exception(f"Job {job_number} has no places.")
    output = []
    for job_record in my_job_records:
        place_record = Place.query.filter(Place.id == job_record.placeid).first().__dict__ 
        google_record = PlaceGoogle.query.filter(PlaceGoogle.id == place_record['placegoogleid']).first()
        place_record['website'] = google_record.website
        output.append(place_record)
    return output

@bp.route('/download/<int:job_number>', methods=('GET',))
def download_report(job_number):
    error = None
    job = JobList.query.filter(JobList.id == job_number).first()
    if job is None:
        error = 'Could not find that job.'
        abort(404, error)

    #proxyIO = io.StringIO()
    mem = io.BytesIO()
    data = rawreport(job_number).create_report()
    converter = Converter()
    converter.convert(data, Writer(mem))
    mem.seek(0)
    return_file = send_file(mem, attachment_filename='uscope.xlsx', as_attachment=True, cache_timeout=0)
    return_file.mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    return return_file



        
    

    

        
            
        