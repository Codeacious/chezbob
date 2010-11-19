import base64, cgi, datetime, math
from decimal import Decimal
from time import strptime

from django.shortcuts import render_to_response, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, HttpResponseRedirect

##### Available queries to run #####
queries = {}
query_order = []
def add_query(name, description, query, variables):
    queries[name] = {"name": name,
                     "description": description,
                     "query": query,
                     "variables": [x[0] for x in variables],
                     "defaults": [x[1] for x in variables],
                     "param_info": [{'name': x[0], 'default': x[1]}
                                    for x in variables]}
    query_order.append(name)

add_query("accounts", "Account Balances",
          """select username, balance, last_seen, email
             from account_summary order by balance, lower(username)""",
          [])

add_query("accounts_inactive", "Inactive Accounts",
          """select username, balance, last_seen, email
             from account_summary
             where last_seen is null or last_seen < now() - interval %s
             order by last_seen, lower(username)""",
          [('interval', '2 year')])

add_query("inactive", "Newly-Inactive Products",
          """select * from bulk_items
             where
               bulkid not in
                 (select distinct bulkid from aggregate_purchases
                  where date >= %s and bulkid is not null)
               and active
             order by description""",
          [('date', datetime.date.today() - datetime.timedelta(30))])

add_query("newactive", "Recently-Purchased But Not Active Products",
          """select * from bulk_items
             where
               bulkid in
                 (select distinct bulkid from aggregate_purchases
                  where date >= %s and bulkid is not null)
               and not active
             order by description""",
          [('date', datetime.date.today() - datetime.timedelta(30))])

add_query("products", "All Products",
          """select * from products""",
          [])

add_query("deposits", "Cash Deposits and Refunds",
          """select username, xacttime, xactvalue, xacttype, source
             from transactions join users using (userid)
             where xacttype in ('ADD', 'REFUND')
             order by xacttime""",
          [])

add_query("transactions", "User Transaction Log",
          """select xacttime, xactvalue, source,
                    substring(xacttype from '^[^ ]*') as xacttype
             from transactions join users using (userid)
             where username = %s
             order by xacttime""",
          [('username', '')])

##### Helper functions #####
def run_query(query, variables):
    """Run an SQL query directly against the database and return results.

    Returns a pair containing information about each database column, and the
    set of database results."""

    from django.db import connection
    cursor = connection.cursor()
    cursor.execute(query['query'], variables)

    columns = [c[0] for c in cursor.description]
    data = cursor.fetchall()

    return {'query': query, 'columns': columns, 'data': data}

# Execute a query and return the results as an HTML table.
def generate_table(query_name, request):
    query = queries[query_name]
    variables = []
    for v in query['variables']:
        if v in request.GET:
            variables.append(request.GET[v])
        else:
            variables.append('')        # TODO: Sensible defaults
    results = run_query(query, variables)

    yield "<table>\n"
    yield "<thead>\n"
    yield "<tr>\n"
    for c in results['columns']:
        yield "<th>" + cgi.escape(c) + "</th>\n"
    yield "</tr>\n"
    yield "</thead>\n"

    yield "<tbody>\n"
    for row in results['data']:
        yield "<tr>\n"
        for d in row:
            yield "<td>" + cgi.escape(str(d)) + "</td>\n"
        yield "</tr>\n"
    yield "</tbody>\n"

    yield "</table>\n"

##### Page view functions (invoked by Django to display a page) #####
@login_required
def home(request):
    all_queries = [queries[n] for n in query_order]

    return render_to_response('query/home.html',
                              {'user': request.user, 'queries': all_queries})

def results(request, query):
    table = "".join(generate_table(query, request))

    return render_to_response('query/results.html',
                              {'user': request.user, 'raw_table': table})

@login_required
def raw_table(request, query):
    """Return results as a raw HTML table.

    This isn't meant to be displayed directly, but instead included as part of
    a larger page by JavaScript code to dynamically generate a results page."""

    response = HttpResponse(mimetype="text/html")
    for line in generate_table(query, request):
        response.write(line)
    return response

