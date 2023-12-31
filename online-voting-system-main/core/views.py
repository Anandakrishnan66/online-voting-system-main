from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from core.models import Election, Candidate, Result
from django.contrib import messages
import datetime as dt
from django.db.models import Sum, Max


#HomevIew
def index(request):
    return render(request, "core/home.html")

#Current Election View
@login_required(login_url='login')
def current_election(request):
    elect_data = Election.objects.filter(election_state=request.user.state, is_active=True)

    return render(request, "core/current_election.html", {"elect_data":elect_data})

# Election Detail View
@login_required(login_url='login')
def election_detail(request, election_idd):
    # Check if election exist
    election = get_object_or_404(Election, election_uid=election_idd, election_state = request.user.state)

    # Setting election active status
    election_days_left = election.end_date - dt.date.today()
    if election_days_left.days < 0:
        election.is_active = False
        election.save()

    #Filtering candidates by election
    candidates = Candidate.objects.filter(cand_election=election, cand_const=request.user.constituency)

    # check if user voted
    is_voted = Result.objects.filter(voter=request.user, election=election)

    context = {
        "election":election,
        "candidates":candidates,
        "election_days_left":election_days_left.days,
        "is_voted":is_voted
    }

    return render(request, "core/election_detail.html", context=context)

#Candidate View
def candidate(request, candidate_idd):

    #Check if candidate exist
    candidate = get_object_or_404(Candidate, candidate_uid=candidate_idd)

    return render(request, "core/candidate.html", {"candidate":candidate})

#Voting Process View
@login_required(login_url='login')
def voting_process(request, election_idd):

    # Check if election exist
    election = get_object_or_404(Election, election_uid=election_idd, is_active=True)

    # Setting election active status
    election_days_left = election.end_date - dt.date.today()
    if election_days_left.days < 0:
        election.is_active = False
        election.save()

    #Getting form fields
    if request.method == 'POST':
        cand_id = request.POST['cand-id']

        filter_candidate = Candidate.objects.filter(candidate_uid=cand_id)

        if filter_candidate:
            candidate = Candidate.objects.get(candidate_uid=cand_id)
            #Casting Vote
            caste_vote = Result(
                voter = request.user,
                candidate = candidate,
                election = election
            )
            candidate.total_votes = candidate.total_votes + 1
            caste_vote.save()
            candidate.save()
            messages.success(request, "Successfully Registered Vote.")
        else:
            messages.error(request, "Candidate doesn't exist")


    #Checking if user casted vote
    is_voted = Result.objects.filter(voter=request.user.id, election=election)

    #filter candidate by election
    get_candidate = Candidate.objects.filter(cand_election=election, cand_const=request.user.constituency)

    context = {
        "candidates":get_candidate,
        "is_voted":is_voted,
        "election":election
    }

    return render(request, "core/voting_process.html", context=context)

#Election Result View
def election_result(request, election_idd):

    # Check if election exist
    election = get_object_or_404(Election, election_uid=election_idd)

    #Election days left
    election_days_left = election.end_date - dt.date.today()

    #Calculating no. of candidates and total votes of all candidates
    candidates = Candidate.objects.filter(cand_election=election)

    max_vote = Candidate.objects.filter(cand_election=election).aggregate(maxVote=Max('total_votes'))['maxVote']

    leading_candidate = Candidate.objects.filter(cand_election=election, total_votes=max_vote)

    context = {
        "election":election,
        "candidates":candidates,
        "election_days_left":election_days_left.days,
        "total_votes":candidates.aggregate(Sum('total_votes'))['total_votes__sum'],
        "leading_candidate":leading_candidate,
    }

    return render(request, "core/election_result.html", context=context)

def election_result_user(request, election_idd):
    
    # Check if election exist
    election = get_object_or_404(Election, election_uid=election_idd)

    #Election days left
    election_days_left = election.end_date - dt.date.today()

    #Calculating no. of candidates and total votes of all candidates
    candidates = Candidate.objects.filter(cand_election=election)

    max_vote = Candidate.objects.filter(cand_election=election).aggregate(maxVote=Max('total_votes'))['maxVote']

    leading_candidate = Candidate.objects.filter(cand_election=election, total_votes=max_vote)

    context = {
        "election":election,
        "candidates":candidates,
        "election_days_left":election_days_left.days,
        "total_votes":candidates.aggregate(Sum('total_votes'))['total_votes__sum'],
        "leading_candidate":leading_candidate,
    }

    return render(request, "core/election_result_user.html", context=context)

#Result View
def result(request):
    elect_data = Election.objects.all()
    a=Candidate.objects.all()
    return render(request, "core/result.html", {"elect_data":elect_data})

