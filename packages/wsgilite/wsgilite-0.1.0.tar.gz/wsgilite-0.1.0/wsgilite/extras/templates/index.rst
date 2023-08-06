Index of `{{ baseurl }}`
==========={{ "=" * (baseurl|count) }}

.. serving: {{ fsdir }}

{# {% for item in items %}
 - `{{ item.filename }} <{{ item.link_path }}>`_

    - {{ item.date }}
{% endfor %} #}
{{ tabulate('tablelist.rst', items, ('filename', 'links', 'date', 'content_type')) }}
