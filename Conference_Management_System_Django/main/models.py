from django.db import models
from django.utils import timezone
from main import constants


#entities
class User(models.Model):
    user_id = models.TextField(null=False,primary_key=True)
    login_email = models.TextField(null=False)
    login_pw = models.TextField(null=False)
    name = models.TextField(null=False)
    is_suspended = models.BooleanField(default=False)
    user_type = models.TextField(null=False)                    #0 = system admin
                                                                #1 = conference chair
                                                                #2 = reviewer
                                                                #3 = author
    
class Paper(models.Model):
    paper_id = models.TextField(null=False,primary_key=True)
    paper_name = models.TextField(default="")
    paper_details = models.TextField(default="")
    acceptance_state = models.TextField(default=0)              #0 = unsubmitted/pending
                                                                #1 = unaccepted
                                                                #2 = accepted
    
class Reviewer(models.Model):
    user_id = models.ForeignKey('User',on_delete=models.CASCADE)
    max_papers = models.TextField(default=5)
    
    
    
#relationships
class Bids(models.Model):
    reviewer_id = models.ForeignKey('User',on_delete=models.CASCADE)
    paper_id = models.ForeignKey('Paper',on_delete=models.CASCADE)
    is_bidding = models.BooleanField(default=True)

class Authors(models.Model):
    author_id = models.ForeignKey('User',on_delete=models.CASCADE)
    paper_id = models.ForeignKey('Paper',on_delete=models.CASCADE)

class Reviews(models.Model):
    review_id = models.TextField(null=False,primary_key=True)
    paper_id = models.ForeignKey('Paper',on_delete=models.CASCADE)
    reviewer_id = models.ForeignKey('User',on_delete=models.CASCADE)
    review_details = models.TextField(null=False)
    reviewer_rating = models.TextField(null=False)
    author_rating = models.TextField(null=False)
    
class ReviewComments(models.Model):
    comment_id = models.TextField(null=False,primary_key=True)
    review_id = models.ForeignKey('Reviews',on_delete=models.CASCADE)
    commenter_id = models.ForeignKey('User',on_delete=models.CASCADE)
    comment_text = models.TextField(null=False)
    
    # type = models.TextField(null=False)
    # end_date = models.DateTimeField(null=False)
    # is_accepted = models.BooleanField(default=False)
    # author = models.ForeignKey('Author',on_delete=models.CASCADE)