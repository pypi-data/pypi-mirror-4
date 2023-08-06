
{% block filename %}
{% if baseurl == '/' %}
    {% set linkurl = '' %}
{% else %}
    {% set linkurl = baseurl.rstrip('/') %}
{% endif %}
`{{ row.filename }}{{ '/' if row.isdir else '' }} <{{linkurl}}/{{ row.filename }}>`_
{# `{{ row.filename }} <{{ row.link_path }}>`_ #}
{% endblock %}


{% block date %}
{{ row.date }}

{% endblock %}


{% block content_type %}
{{ row.content_type or ('DIR' if row.isdir else 'unknown file type') }}
{% endblock %}


{% block links %}
...
{% endblock %}
