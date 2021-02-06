from datetime import datetime
from random import randint

from models import jobPosting, Users


def random_with_N_digits(n):
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1
    return randint(range_start, range_end)


def savejobPosting(title: str,
                   description: str,
                   location: [float],
                   expiryDate: str,
                   ):
    jobPosting(id=jobPosting.objects.count() + 1,
               title=title,
               description=description,
               location=location,
               whoApplied=[],
               expiryDate=expiryDate).save()


def appendApplicants_jobPosting(id: str, applicant_email: str):
    jobPost = jobPosting.objects(id=id)[0]
    if applicant_email not in jobPost['whoApplied']:
        jobPost['whoApplied'].append(applicant_email)
        jobPost.save()


def editProfile(id: str, **kwargs: dict):
    user = Users().objects(id=id).update(**kwargs)


def getJobs(id: int = 0):
    job = []
    if id and id != 0:
        job = jobPosting.objects(id=int(id))
        if job:
            job = job[0]
    else:
        job = jobPosting.objects()

    return job
