from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.template import RequestContext
from polls.models import Poll
from polls.helpers import *


def list(request):
    objects = Poll.objects.all()
    return render_to_response("poll_list.html", {"objects": objects}, context_instance=RequestContext(request))


@csrf_protect
def detail(request, poll_id):
    error_msg = None
    poll = get_object_or_404(Poll, pk=poll_id)
    page_index = 0

    if poll.id in request.session:
        page_index = request.session[poll.id]["current_page"]
    else:
        request.session[poll.id] = {}
        request.session[poll.id]["current_page"] = page_index
        request.session.modified = True

    if request.method == "POST":
        page_index = int(request.POST["current_page_index"])
        request.session[poll.id]["current_page"] = page_index
        request.session.modified = True

        valid = page_valid(request.POST, poll.get_questions_from_page(page_index))
        if valid:
            save_answers(request, poll.id, page_index)
            if "next_page_index" in request.POST:
                page_index = int(request.POST["next_page_index"])
                request.session[poll.id]["current_page"] = page_index
                request.session.modified = True
            else:
                request.session[poll.id]["current_page"] = "result"
                request.session.modified = True
                return render_to_response("poll_result.html", compute_results(request, poll), context_instance=RequestContext(request))
        else:
            error_msg = "Select at least one answer for each question"

    if page_index == "result":
        return render_to_response("poll_result.html", compute_results(request, poll), context_instance=RequestContext(request))

    questions = []

    if poll.page_set.all().count() != 0 and poll.get_questions_from_page(int(page_index)).count() != 0:
        questions = poll.get_questions_from_page(int(page_index))

    response_dict = {
        "poll": poll,
        "error_msg": error_msg,
        "page_index": page_index,
        "questions": questions
    }
    return render_to_response("poll_detail.html", response_dict, context_instance=RequestContext(request))
