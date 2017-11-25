
from __future__ import unicode_literals


from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from models import User, Travel
from django.db.models import Q


def index(request):
    return render(request, "travel_app/index.html")


def register(request):
    result = User.objects.validate_reg(request.POST)
    if result["success"] == False:
        for error in result["errors"]:
            messages.error(request, error)
        return redirect("/")
    else:
        request.session['user_id'] = result['user'].id
        return redirect('/travels')


def login(request):
    result = User.objects.validate_login(request.POST)
    if result["success"] == False:
        for error in result['errors']:
            messages.error(request, error)
        return redirect('/')
    else:
        request.session['user_id'] = User.objects.get(
            alias=request.POST['username']).id
        return redirect('/travels')


def logout(request):
    if 'user_id' not in request.session:
        messages.error(request, "please sign in before doing that")
        return redirect("/")
    del request.session['user_id']
    return redirect('/')


def travels_add(request):
    return render(request, 'travel_app/addtravels.html')


def travel_create(request):
    user_id = request.session['user_id']
    result = Travel.objects.validate_create(request.POST, user_id)
    if result['success'] == False:
        for error in result['errors']:
            messages.error(request, error)
        return redirect('/travels/add')
    return redirect('/travels')


def travels(request):
    if 'user_id' not in request.session:
        messages.error(request, "please sign in before doing that")
        return redirect("/")
    user_id = request.session['user_id']
    user = User.objects.get(id=user_id)
    travelLog = []
    try:
        travel_created = Travel.objects.get(
            id=user.travel_created.values('id'))
        travelLog.append(travel_created)
    except:
        print "user had no created travels"
    # get travel join ids
    travel_join_ids = user.travel_join.all().values('id')
    print travel_join_ids
    for travel in travel_join_ids:
        travelLog.append(Travel.objects.get(id=travel['id']))

    otherUsers = User.objects.filter(~Q(id=user_id))
    allOtherUsersTravels = []
    for user in otherUsers:
        allOtherUsersTravels.append(
            user.travel_created.all().values('creator'))
    otherUsersTravelLog = []
    # get the other users travel log
    for travels in allOtherUsersTravels:
        for travel in travels:
            user = User.objects.get(id=travel['creator'])
            travel = Travel.objects.get(id=travel['creator'])
            otherUsersTravelLog.append({
                'user': user,
                'travel': travel
            })
    print 'otherUsersTravelLog'
    print otherUsersTravelLog
    context = {
        'user': User.objects.get(id=request.session['user_id']),
        'travel': travelLog,
        'otherTravel': otherUsersTravelLog
    }
    return render(request, "travel_app/travels.html", context)


def travel_join(request, travel_id):
    user = User.objects.get(id=request.session['user_id'])
    travel = Travel.objects.get(id=travel_id)
    user.travel_join.add(travel)
    travel.join_users.add(user)

    return redirect('/travels')


def travels_view(request, travel_id):
    travel = Travel.objects.get(id=travel_id)
    joined_users = travel.join_users.all().values('id')
    joined_user_list = []
    for user in joined_users:
        joined_user_list.append(User.objects.get(id=user['id']))
    context = {
        'travel': travel,
        'joined_list': joined_user_list
    }
    return render(request, "travel_app/travel_view.html", context)
