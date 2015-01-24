import datetime

from browser import html

answers = list(zip([1, 0, -1], ['בעד', 'נמנע', 'נגד']))

short_name_of_long_name = {
  'חזית דמוקרטית לשלום ושוויון': 'חד”ש',
  'ברית לאומית דמוקרטית': 'בל”ד',
  }

no_result_text = '''
    ענו על שאלות כדי לצפות בתוצאות.
    ככל שתענו על מספר רב יותר של שאלות, תקבלו תוצאה מדוייקת יותר.
    '''

def question_panel(data):
    outer_frame = html.DIV(id='q%d'%data['id'], Class='question-box')
    panel = html.DIV()
    outer_frame <= panel

    against = html.DIV()
    in_favor = html.DIV()
    content = html.DIV()
    skip = html.DIV()
    party_votes_doc = html.DIV(id='q%d_party_votes'%data['id'], Class='table-responsive')

    panel <= html.LABEL(against, Class='answer-button answer-against')
    panel <= html.LABEL(in_favor, Class='answer-button answer-for')
    panel <= content
    panel <= html.LABEL(skip, Class='answer-skip')
    panel <= party_votes_doc

    against_radio = html.INPUT(type='radio', name=str(data['id']), value='-1')
    skip_radio = html.INPUT(type='radio', name=str(data['id']), value='0')
    for_radio = html.INPUT(type='radio', name=str(data['id']), value='1')

    against <= against_radio
    against <= html.DIV('נגד')
    against <= html.DIV(
        html.SPAN(Class='glyphicon glyphicon-arrow-left',
            style={'float': 'right', 'padding-right': '2px'}))
    against <= html.DIV(style={'clear': 'both', 'height': '5px'})

    in_favor <= for_radio
    in_favor <= html.DIV('בעד')
    in_favor <= html.DIV(
        html.SPAN(Class='glyphicon glyphicon-arrow-right',
            style={'float': 'left', 'padding-left': '2px'}))
    in_favor <= html.DIV(style={'clear': 'both', 'height': '5px'})

    skip <= skip_radio
    skip <= html.SPAN('לא בטוח? ')
    skip <= html.SPAN('דלג לשאלה הבאה', style={'text-decoration': 'underline'})

    title = data.get('vt_title')
    if not title:
        title = data['title']
        for prefix in [
            'להעביר את הצעת החוק לוועדה - ',
            'להעביר את הצעת החוק לוועדה שתקבע ועדת הכנסת - ',
            'הצבעה -',
            ]:
            if title.startswith(prefix):
                title = title[len(prefix):]
                break
    content <= html.H3(title)

    description = data.get('vt_description') or data['summary']
    too_long = 700
    if description and len(description) > too_long:
        tooltip = description
        # it is silly to open the tooltip for one extra word..
        cut_at = too_long - 200
        description = description[:cut_at]+'...'
    else:
        tooltip = None
    if tooltip:
        summary = html.P(
            tooltip=tooltip.replace('<br>', ' '),
            Class='has-tooltip')
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
        'מידע נוסף',
        target='_blank',
        href='https://oknesset.org/vote/%d/' % data['id'],
        )
    content <= summary
    return outer_frame, party_votes_doc, [against_radio, skip_radio, for_radio]

def question_party_votes(party_votes_doc, data, user_answer):
    def key(x):
        results = x[1]
        return x[0]
    table = html.TABLE(
        style={'text-align': 'center', 'background': '#f9f9f9'},
        Class='table table-packed')
    party_votes_doc <= table
    parties_row = html.TR(html.TH('מפלגה', style={'vertical-align': 'top'}))
    table <= html.THEAD(parties_row)
    tbody = html.TBODY()
    table <= tbody
    rows = {}
    for (v, name) in answers:
        if not v:
            continue
        style = {}
        if user_answer:
            style['background'] = ['#ffdddd', '#ccfacc'][v == user_answer]
        elif not rows:
            style['background'] = 'white'
        row = html.TR(html.TH(name), style=style)
        tbody <= row
        rows[v] = row
    for party_name, results in sorted(data['party_votes'].items(), key=key):
        [for_txt, vs_txt] = [
            '%.0f%%'%(100*r) if r else '-'
            for r in [results.get('for'), results.get('against')]]
        short_name = short_name_of_long_name.get(party_name, party_name)
        for row, val in [
            (parties_row, short_name),
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
        s = {}
        for k in [-1, 1]:
            s[k] = sum(x[k] for x in t) / len(t)
        s['overall'] = s[1] - s[-1]
        results[party_name] = s
    return results, num_answers

def render_results(results_dest, results_small, progress_dest, res):
    (results, num_answers) = res

    if num_answers == 1:
        progress_text = 'ענית על שאלה אחת'
    else:
        progress_text = 'ענית על %d שאלות' % num_answers
    num_questions_to_answer = 10
    progress_width = min(100, 100/num_questions_to_answer*num_answers)
    progress_dest <= html.DIV(
        html.DIV(progress_text,
            Class='progress-bar progress-bar-success', role='progressbar',
            style={
                'min-width': '10em',
                'width': '%d%%' % progress_width,
                'float': 'right',
                }),
        Class='progress')

    results_table = html.TABLE(Class='table table-striped')
    results_dest <= results_table
    header_row = html.TR()
    header_row <= html.TH('מקום', style={'text-align': 'right'})
    header_row <= html.TH('מפלגה', style={'text-align': 'right'})
    header_row <= html.TH('איתך')
    header_row <= html.TH('נגדך')
    header_row <= html.TH('סה״כ')
    results_table <= html.THEAD(header_row)
    table_body = html.TBODY()
    results_table <= table_body

    if not results:
        table_body <= html.TR(html.TD(no_result_text, colspan=5))
        return

    results_small <= html.B('תוצאות:')

    def key(x):
        return (-x[1]['overall'], x[0])
    prev_score = None
    for idx, (party_name, score) in enumerate(sorted(list(results.items()), key=key)):
        if idx == 0 or score['overall'] < prev_score['overall']:
            pos = idx+1
        prev_score = score

        row = html.TR()
        short_name = '%d. %s' % (
            pos, short_name_of_long_name.get(party_name, party_name))
        pos_txt = str(pos)
        results_small <= html.BR()
        results_small <= short_name
        row <= html.TD(pos_txt)
        row <= html.TD(party_name)
        for k in [1, -1, 'overall']:
            cell = '%.0f%%'%(100*score[k])
            row <= html.TD(cell, dir='ltr')
        table_body <= row

    if num_answers > 0:
        results_dest <= html.A('התחל מההתחלה', href='/restart/')

    results_dest <= html.BR()
