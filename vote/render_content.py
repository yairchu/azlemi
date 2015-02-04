import datetime

from browser import html

answers = list(zip([1, 0, -1], ['בעד', 'נמנע', 'נגד']))

def make_texts():
    def _(x):
        return x
    return {
        'no_result': _('''
            ענו על שאלות כדי לצפות בתוצאות.
            ככל שתענו על מספר רב יותר של שאלות, תקבלו תוצאה מדוייקת יותר.
            '''),
        'against': _('נגד'),
        'for': _('בעד'),
        'unsure': _('לא בטוח'),
        'skip': _('דלג לשאלה הבאה'),
        'more_info': _('מידע נוסף'),
        'party': _('מפלגה'),
        'pos': _('מקום'),
        'answered': _('ענית על'),
        'question': _('שאלה'),
        'questions': _('שאלות'),
        'one': _('אחת'),
        'results': _('תוצאות'),
        'details': _('ראה פירוט ←'),
        'details_share': _('ראה פירוט ושתף! ←'),
        'new_parties_footnote': _('* מפלגות שרק מועמד אחד או שניים מתוכם היו בכנסת. המידע עליהם לא בהכרח מייצג מהימנה את שאר חברי המפלגה'),
        'share': _('שתף את התוצאות שלי!'),
        'scoring': _('איך נקבע הניקוד?'),
        'restart': _('התחל מההתחלה (אפס מצב)'),
        'party': _('מפלגה'),
        'good': _('איתך'),
        'bad': _('נגדך'),
        'total': _('סה״כ'),
        'align_right': _('right'),
        'lang_prefix': _('/'),
        }
texts = make_texts()

def question_panel(data, _):
    outer_frame = html.DIV(id='q%d'%data['id'], Class='question-box')
    panel = html.DIV()
    outer_frame <= panel

    against = html.DIV()
    in_favor = html.DIV()
    content = html.DIV()
    skip = html.DIV()
    party_votes_doc = html.DIV(id='q%d_party_votes'%data['id'], Class='table-responsive')

    panel <= html.LABEL(against, Class='answer answer-button answer-against')
    panel <= html.LABEL(in_favor, Class='answer answer-button answer-for')
    panel <= content
    panel <= html.LABEL(skip, Class='answer answer-skip')
    panel <= party_votes_doc

    against_radio = html.INPUT(type='radio', name=str(data['id']), value='-1')
    skip_radio = html.INPUT(type='radio', name=str(data['id']), value='0')
    for_radio = html.INPUT(type='radio', name=str(data['id']), value='1')

    against <= against_radio
    against <= html.DIV(_(texts['against']))
    against <= html.DIV(
        html.SPAN(Class='glyphicon glyphicon-arrow-left',
            style={'float': 'right', 'padding-right': '2px'}))
    against <= html.DIV(style={'clear': 'both', 'height': '5px'})

    in_favor <= for_radio
    in_favor <= html.DIV(_(texts['for']))
    in_favor <= html.DIV(
        html.SPAN(Class='glyphicon glyphicon-arrow-right',
            style={'float': 'left', 'padding-left': '2px'}))
    in_favor <= html.DIV(style={'clear': 'both', 'height': '5px'})

    skip <= skip_radio
    skip <= html.SPAN(_(texts['unsure'])+'? ')
    skip <= html.SPAN(_(texts['skip']), style={'text-decoration': 'underline'})

    content <= html.H3(data['title'])

    description = data['summary']
    too_long = 700
    if description and len(description) > too_long:
        # it is silly to open the tooltip for one extra word..
        cut_at = len(description[:too_long - 200].rsplit(' ', 1)[0])+1
        tooltip = description[cut_at:]
        description = description[:cut_at]+'...'
    else:
        tooltip = None
    if tooltip:
        summary = html.P(**{
            'data-original-title': tooltip,
            'data-toggle': 'tooltip',
            'data-placement': 'bottom',
            'data-html': 'true',
            })
    else:
        summary = html.P()
    if description:
        first_block = True
        for block in description.split('<br>'):
            if not block.strip():
                continue
            if first_block:
                first_block = False
            else:
                summary <= html.BR()
            summary <= block
        summary <= ' '
    if tooltip:
        summary <= html.BR()
    summary <= html.A(
        _(texts['more_info']),
        target='_blank',
        href='https://oknesset.org/vote/%d/' % data['id'],
        )
    content <= summary
    return outer_frame, party_votes_doc, [against_radio, skip_radio, for_radio]

def question_party_votes(party_votes_doc, data, user_answer, _):
    def key(x):
        results = x[1]
        return x[0]
    table = html.TABLE(
        style={'text-align': 'center', 'background': '#f9f9f9'},
        Class='table table-packed')
    party_votes_doc <= table
    parties_row = html.TR(
        html.TH(_(texts['party']), style={'vertical-align': 'top'}))
    table <= html.THEAD(parties_row)
    tbody = html.TBODY()
    table <= tbody
    rows = {}
    for (v, name) in answers:
        if not v:
            continue
        style = {}
        if user_answer or not rows:
            style['background'] = 'white'
        if v == user_answer:
            style['color'] = '#07f'
            style['font-weight'] = 'bold'
        elif user_answer:
            style['color'] = '#666'
        row = html.TR(html.TH(_(name)), style=style)
        tbody <= row
        rows[v] = row
    for party_name, results in sorted(data['party_votes'].items(), key=key):
        [for_txt, vs_txt] = [
            '%.0f%%'%(100*r) if r else '-'
            for r in [results.get('for'), results.get('against')]]
        for row, val in [
            (parties_row, _(party_name)),
            (rows[1], for_txt),
            (rows[-1], vs_txt),
            ]:
            row <= html.TD(val)

def calc_results(questions, user_answers):
    results = {}
    num_answers = 0
    for qid, answer in user_answers.items():
        if not answer:
            continue
        num_answers += 1
        question = questions[qid]
        for party_name, votes in question['party_votes'].items():
            vote_results = {-1: 0, 1: 0}
            for k, v in votes.items():
                vote_vals = {'for': 1, 'against': -1}
                if k not in vote_vals:
                    continue
                vote_results[vote_vals[k] * answer] += v
            results.setdefault(party_name, []).append(vote_results)
    for party_name, t in results.items():
        num_answers_where_party_exists = len(t)
        num_answers_without_party = num_answers - num_answers_where_party_exists
        divisor = num_answers_where_party_exists + num_answers_without_party/2
        s = {}
        for k in [-1, 1]:
            s[k] = sum(x[k] for x in t) / divisor
        s['overall'] = s[1] - s[-1]
        results[party_name] = s
    return results, num_answers

def sorted_results(results):
    def key(x):
        return (-x[1]['overall'], x[0])
    prev_score = None
    for idx, (party_name, score) in enumerate(sorted(list(results.items()), key=key)):
        if idx == 0 or score['overall'] < prev_score['overall']:
            pos = idx+1
        prev_score = score
        yield pos, party_name, score

party_links = {
    'הליכוד': 'https://www.likud.org.il/',
    'המחנה הציוני': 'http://www.hamahanehazioni.co.il/',
    'יש עתיד': 'http://yeshatid.org.il/',
    'ישראל ביתנו': 'http://www.beytenu.org.il/',
    'הבית היהודי': 'http://www.baityehudi.org.il',
    'ש”ס': 'http://shas.org.il/',
    'יהדות התורה': 'https://he.wikipedia.org/wiki/יהדות_התורה',
    'מרצ': 'http://meretz.org.il/',
    'הרשימה המשותפת': 'https://he.wikipedia.org/wiki/הרשימה_המשותפת',
    'כולנו': 'https://www.kulanu-party.co.il/',
    'יחד': 'https://he.wikipedia.org/wiki/יחד_בראשות_אלי_ישי',
    'הרשימה הערבית': 'https://he.wikipedia.org/wiki/הרשימה_הערבית',
    }

def render_results_table(results, _):
    results_table = html.TABLE(Class='table table-striped')
    header_row = html.TR()
    header_row <= html.TH(_(texts['pos']), style={'text-align': _(texts['align_right'])})
    header_row <= html.TH(_(texts['party']), style={'text-align': _(texts['align_right'])})
    header_row <= html.TH(_(texts['good']))
    header_row <= html.TH(_(texts['bad']))
    header_row <= html.TH(_(texts['total']))
    results_table <= html.THEAD(header_row)
    table_body = html.TBODY()
    results_table <= table_body
    if not results:
        table_body <= html.TR(html.TD(_(texts['no_result']), colspan=5))
        return results_table
    for pos, party_name, score in sorted_results(results):
        row = html.TR()
        row <= html.TD(str(pos))
        link = party_links.get(party_name.strip('*'))
        if link:
            party_name = html.A(_(party_name), target='_blank', href=link)
        row <= html.TD(party_name)
        for k in [1, -1, 'overall']:
            cell = '%.0f%%'%(100*score[k])
            row <= html.TD(cell, dir='ltr')
        table_body <= row
    return results_table

def render_results(results_dest, results_small_dest, progress_dest, progress_circle_dest, res, user_answers, _):
    (results, num_answers) = res

    if num_answers == 1:
        progress_text_lines = [
            _(texts['answered']),
            _(texts['question']),
            _(texts['one']),
            ]
    else:
        progress_text_lines = [_(texts['answered']), str(num_answers), _(texts['questions'])]
    num_questions_to_answer = 12
    progress = min(1, num_answers/num_questions_to_answer)
    progress_dest <= html.DIV(
        html.DIV(' '.join(progress_text_lines),
            Class='progress-bar progress-bar-success', role='progressbar',
            style={
                'min-width': '10em',
                'width': '%d%%' % (100*progress),
                'float': _(texts['align_right']),
                }),
        Class='progress')

    results_dest <= render_results_table(results, _)

    progress_rotate = 'rotate(%ddeg)' % (180+360*progress)
    circle_fill_style = {
        'transform': progress_rotate,
        '-webkit-transform': progress_rotate,
        '-ms-transform': progress_rotate,
        'background-color': '#eee',
        }
    radial_progress_style = {}
    progress_color = '#fd7f19'
    if progress <= 0.5:
        circle_fill_style['background-color'] = progress_color
        progress_clip = 'rect(0px, 150px, 150px, 75px)'
    else:
        radial_progress_style['background-color'] = progress_color
        progress_clip = 'rect(0px, 75px, 150px, 0px)'
    circle_fill_style['clip'] = progress_clip
    radial_progress = html.DIV(Class='radial-progress', style=radial_progress_style)
    progress_circle_dest <= radial_progress
    circle_fill = html.DIV(Class='fill', style=circle_fill_style)
    radial_progress <= html.DIV(
        html.DIV(circle_fill, Class='mask', style={'clip': progress_clip}),
        Class='circle')
    radial_progress_inset = html.DIV(Class='inset', style={'color': progress_color})
    for i, t in enumerate(progress_text_lines):
        if i > 0:
            radial_progress_inset <= html.BR()
        radial_progress_inset <= html.B(t)
    radial_progress <= radial_progress_inset

    if not results:
        return

    if progress >= 1:
        results_small_style = {'color': 'black'}
    else:
        x = 255 * (1-progress)
        results_small_style={
            'color': 'rgba(0,0,0,0.0)',
            'text-shadow': '0 0 %fpx rgb(%d,%d,%d)' %
                (4 * (1-progress), x, x, x),
            }
    results_small = html.DIV(style=results_small_style)
    results_small_dest <= results_small
    results_small <= html.B(_(texts['results'])+':')

    for pos, party_name, score in sorted_results(results):
        results_small <= html.BR()
        results_small <= '%d. %s' % (pos, _(party_name))

    results_small <= html.BR()
    if progress < 1:
        results_small <= _(texts['details'])
    else:
        results_small <= _(texts['details_share'])

    results_dest <= _(texts['new_parties_footnote'])
    results_dest <= html.BR()

    if num_answers >= num_questions_to_answer:
        votes_str = ''.join(
            'q%d%s'%(k, 'f' if v == 1 else 'a') for k, v in sorted(user_answers.items()) if v)
        results_dest <= html.FORM(
            html.INPUT(
                value=_(texts['share']),
                type="submit", Class='btn btn-lg btn-success'),
            method='post',
            action=_(texts['lang_prefix'])+'publish/%s/'%votes_str,
            style={'text-align': 'center', 'margin': '5px'})

    results_dest <= html.A(_(texts['scoring']), target='_blank', href='/scoring')
    results_dest <= html.BR()
    results_dest <= html.A(_(texts['restart']), href=_(texts['lang_prefix'])+'restart/')
    results_dest <= html.BR()
