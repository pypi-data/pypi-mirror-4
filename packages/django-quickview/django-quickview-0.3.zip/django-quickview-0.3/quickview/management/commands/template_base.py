
def get_templates(app_label, model_name):
    model_name_uc = model_name
    app_label = app_label.lower()
    model_name = model_name.lower()
    index_template = """{% extends '[[app_label]]/[[model_name]]/base_site.html' %}
    {% block extrahead %}
    <script>
        function delete[[model_name]]([[model_name]]_id)
        {
            [[model_name]]Api.delete([[model_name]]_id);
            jQuery('#[[model_name]]_' + [[model_name]]_id).hide('slow');
        }
    </script>
    {% endblock %}

    {% block content %}

    {% for object in object_list %}
    <div id="[[model_name]]_{{object.id}}">
        <h3><a href="{% url '[[app_label]]-[[model_name]]-detail' object.id %}">{{ object }}</a></h3>
        <ul>
            <li><a href="{% url '[[app_label]]-[[model_name]]-delete' object.id %}">Delete {{ object }}</a></li>
            <li><a href="{% url '[[app_label]]-[[model_name]]-update' object.id %}">Update {{ object }}</a></li>
            <li><a href="{% url '[[app_label]]-[[model_name]]-detail' object.id %}">See details for {{ object }}</a></li>
            <li><a onclick="delete[[model_name]]({{object.id}});">Ajax Delete</a></li>
        </ul>
    </div>
    {% endfor %}

    <div class="pagination">
        <span class="step-links">
            {% if object_list.has_previous %}
                <a href="?page={{ object_list.previous_page_number }}">previous</a>
            {% endif %}

            <span class="current">
                Page {{ object_list.number }} of {{ object_list.paginator.num_pages }}.
            </span>

            {% if object_list.has_next %}
                <a href="?page={{ object_list.next_page_number }}">next</a>
            {% endif %}
        </span>
    </div>
    {% endblock %}""".replace("[[app_label]]", app_label).replace("[[model_name]]", model_name)

    detail_template = """{% extends '[[app_label]]/[[model_name]]/base_site.html' %}

    {% block content %}
    <h1>Details about {{object}}</h1>
    <a href="{% url '[[app_label]]-[[model_name]]-update' object.id %}">Update {{object}}</a>
    {% endblock %}""".replace("[[app_label]]", app_label).replace("[[model_name]]", model_name)

    add_template = """{% extends '[[app_label]]/[[model_name]]/base_site.html' %}

    {% block content %}

    <h1>Add</h1>
    {% if message %}<blockquote>{{ message }}</blockquote>{% endif %}
    <form action="" method="POST">
    {% csrf_token %}
    <table>
    {{ form.as_table }}
    </table>
        <input type="submit">
    </form>

    {% endblock %}""".replace("[[app_label]]", app_label).replace("[[model_name]]", model_name)

    update_template = """{% extends '[[app_label]]/[[model_name]]/base_site.html' %}

    {% block content %}
    <h1>Update {{ object }}</h1>
    <form action="" method="POST">
        <input type="hidden" value="{% url '[[app_label]]-[[model_name]]-detail' object.id %}" name="_redirect_url"> <!-- change _redirect_url to redirect_url to enable -->
    {% csrf_token %}
    <table>
    {{ form.as_table }}
    </table>
        <input type="submit">
    </form>
    {% endblock %}""".replace("[[app_label]]", app_label).replace("[[model_name]]", model_name)

    delete_template = """{% extends '[[app_label]]/[[model_name]]/base_site.html' %}

    {% block content %}
    <h1>Delete {{object}}</h1>
    Are you sure you want to delete {{ object }}?
    <form action="" method="POST">
    {% csrf_token %}
        <input type="hidden" name="pk" value="{{ object.id }}">
        <input type="submit" name="delete" value="Delete">
        <input type="submit" name="cancel" value="Cancel">
    </form>
    {% endblock %}""".replace("[[app_label]]", app_label).replace("[[model_name]]", model_name)

    base_site_template = """{% load quickview_tags %}
<!DOCTYPE html>
<html lang="{% block language_code %}en{% endblock %}">
<head>
    <meta charset="{% block charset %}utf-8{% endblock %}">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{% block description %}{% endblock %}">
    <meta name="author" content="{% block author %}{% endblock %}">
    <title>{% block title %}[[app_label]]{% endblock %}</title>
    <script type="text/javascript" src="{{ STATIC_URL }}js/jquery-1.9.1.min.js"></script>
    <script type="text/javascript" src="{{ STATIC_URL }}js/knockout.js"></script>
    <script type="text/javascript" src="{{ STATIC_URL }}js/handlebars.js"></script>
    <script type="text/javascript" src="{{ STATIC_URL }}js/quickview.js"></script>
    <script type="text/javascript" src="{{ STATIC_URL }}bootstrap/js/bootstrap-tooltip.js"></script>
    <script type="text/javascript" src="{{ STATIC_URL }}bootstrap/js/bootstrap-button.js"></script>
    <script type="text/javascript" src="{{ STATIC_URL }}bootstrap/js/bootstrap-popover.js"></script>
    <script type="text/javascript" src="{{ STATIC_URL }}bootstrap/js/bootstrap-carousel.js"></script>
    <script type="text/javascript" src="{{ STATIC_URL }}bootstrap/js/bootstrap-transition.js"></script>
    <script type="text/javascript" src="{{ STATIC_URL }}bootstrap/js/google-code-prettify/prettify.js"></script>

    <link href="{{ STATIC_URL }}bootstrap/css/bootstrap.css" rel="stylesheet">
    <link href="{{ STATIC_URL }}themes/{% block bootstrap_theme %}readable{% endblock %}/bootstrap.css" rel="stylesheet">
    <!-- it is important to let the line below come after importing the theme or the icons/glyphs from bootstrap won't work -->
    <link href="{{ STATIC_URL }}css/glyphs.css" rel="stylesheet">

    <!-- To change theme insert the line below instead of the line above, using one of the listed themes instead of slate:

        <link href="http://bootswatch.com/slate/bootstrap.min.css" rel="stylesheet">
        - slate
        - united
        - amelia
        - cosmo
        - cyborg
        - journal
        - readable
        - simplex
        - spacelab
        - spruce
        - suprehero

    -->

    {% block extrahead %}
    {% endblock %}
    <style>
        body {
            padding: 50px;
            margin: 50px;
        }
        {% block extrastyle %}
        {% endblock %}
    </style>

    {% quickview_ajax_api [[app_label]] [[model_name]] %}

    <script type="text/javascript">
        {% block extrascript %}
        {% endblock %}

        //<![CDATA[
        $(document).ready(function() {
            {% block documentready %}
            {%  endblock %}
        });
        //]]>
    </script>
</head>
<body>
    <div class="navbar navbar-inverse navbar-fixed-top">
        <div class="navbar-inner">
            <div class="container">
                <a class="brand" href="">{% block branding %}[[app_label]]{% endblock %}</a>
                <div class="nav-collapse collapse">
                    <ul class="nav">
                        <li class="">
                            <a href="{% url '[[app_label]]-[[model_name]]-list' %}">&raquo;&nbsp;List</a>
                        </li>
                        <li class="">
                            <a href="{% url '[[app_label]]-[[model_name]]-add' %}">&raquo;&nbsp;Add</a>
                        </li>
                        {% if user.is_authenticated %}
                        <li class="">
                            <a href="{% url 'logout-view' %}">&raquo;&nbsp;Log out</a>
                        </li>
                        {% else %}
                        <li class="">
                            <a href="{% url 'login-view' %}">&raquo;&nbsp;Log in</a>
                        </li>
                        {% endif %}
                    </ul>
                </div>
            </div>
        </div>
    </div>

    {% block content %}
    {% endblock %}
    </body>
</html>""".replace("[[app_label]]", app_label).replace("[[model_name]]", model_name).replace("[[model_name_uc]]", model_name_uc)

    return index_template, delete_template, add_template, update_template, detail_template, base_site_template
