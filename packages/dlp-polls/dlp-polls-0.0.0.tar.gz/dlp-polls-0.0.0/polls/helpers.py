from polls.models import Answer, PollResultCategory
from operator import attrgetter


def get_answers(poll, selected_answers, total_score, result_categ, better):
    comp_score = total_score
    to_select = {}
    answers_for_selection = []
    if better:
        for page in poll.page_set.all():
            max_q = max([(question, sum([a.score for a in [not_sel for not_sel in question.answer_set.all() if not_sel not in selected_answers and not_sel.score > 0]])) for question in page.question_set.all()], key=lambda item: item[1])[0]
            answers_for_selection += [a for a in max_q.answer_set.all() if a not in selected_answers and a.score > 0]
            # sort answer in order to select a minimum number of answers
        answers_for_selection = sorted(answers_for_selection, key=attrgetter("score"), reverse=True)
    else:
        for page in poll.page_set.all():
            min_q = min([(question, sum([a.score for a in [not_sel for not_sel in question.answer_set.all() if not_sel not in selected_answers and not_sel.score < 0]])) for question in page.question_set.all()], key=lambda item: item[1])[0]
            answers_for_selection += [a for a in min_q.answer_set.all() if a not in selected_answers and a.score < 0]
        # sort answer in order to select a minimum number of answers
        answers_for_selection = sorted(answers_for_selection, key=attrgetter("score"))
    # select answers
    for a in answers_for_selection:
        comp_score += a.score
        if a.question not in to_select:
            to_select[a.question] = []
        to_select[a.question].append(a)
        if better == True and comp_score > result_categ.to_score:
            break
        elif better == False and comp_score < result_categ.from_score:
            break
    return comp_score, to_select


def compute_results(request, poll):
    q_and_a = {}
    total_score = 0
    for key in request.session[poll.id]:
        if key != "current_page":
            for a in request.session[poll.id][key]:
                af = Answer.objects.get(pk=a)
                if not af.question in q_and_a:
                    q_and_a[af.question] = []
                q_and_a[af.question].append(af)
                total_score += af.score

    sorted_categories = sorted(PollResultCategory.objects.filter(poll=poll.id), key=lambda categ: categ.from_score)
    result_categ = None
    for c in sorted_categories:
        if c.from_score <= total_score <= c.to_score:
            result_categ = c
            break

    selected_answers = []
    for k, v in q_and_a.items():
        selected_answers += v

    better = False
    worse = False
    msg = ""
    #for each page compute max/min score of each question using only unselected answers with positive/negative scores only
    comp_score = sum([max([sum([a.score for a in [not_sel for not_sel in question.answer_set.all() if not_sel not in selected_answers and not_sel.score > 0]]) for question in page.question_set.all()]) for page in poll.page_set.all()])
    if comp_score + total_score > result_categ.to_score:
        msg = "Your score might be better if you had selected different answers:"
        better = True

    comp_score = sum([min([sum([a.score for a in [not_sel for not_sel in question.answer_set.all() if not_sel not in selected_answers and not_sel.score < 0]]) for question in page.question_set.all()]) for page in poll.page_set.all()])
    if comp_score + total_score < result_categ.from_score:
        msg += "Your score might be worse if you had selected different answers:"
        worse = True

    if better:
        comp_score, to_select = get_answers(poll, selected_answers, total_score, result_categ, True)
    elif worse:
        comp_score, to_select = get_answers(poll, selected_answers, total_score, result_categ, False)
    else:
        comp_score, to_select = total_score, {}

    return {
    "msg": msg,
    "total_score": total_score,
    "result_categ": result_categ,
    "sel_questions": to_select,
    "poll": poll
    }


def save_answers(request, poll_id, page_idx):
    request.session[poll_id][page_idx] = []
    for key in request.POST:
        if key not in ["next_page_index", "next_page_link", "current_page_index", "csrfmiddlewaretoken", "result_page_link"]:
            request.session[poll_id][page_idx].append(int(request.POST[key]))
    request.session.modified = True


# check if all q have answers set
def page_valid(data, questions):
    for q in questions:
        found = False
        for a in q.answer_set.all():
            if unicode(a.id) in data:
                found = True
                break
        if found == False:
            return False
    return True
