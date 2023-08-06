{% for model_name in model_names %}

function list_{{model_name}}(csrf_token, page, success_handler, failure_handler)
{
    if (page == undefined)
        page = 1;

    var url = "/{{app_label}}/{{model_name}}/list/";
    ajax_call(csrf_token, url, {'page': page}, success_handler, failure_handler);
}

function get_{{model_name}}(csrf_token, {{model_name}}_pk, success_handler, failure_handler)
{
    var params = {'id': {{model_name}}_pk};
    var url = "/{{app_label}}/{{model_name}}/" + {{model_name}}_pk + "/";
    ajax_call(csrf_token, url, params, success_handler, failure_handler);
}

function add_{{model_name}}(csrf_token, params, success_handler, failure_handler)
{
    var url = "/{{app_label}}/{{model_name}}/add/";
    ajax_call(csrf_token, url, params, success_handler, failure_handler);
}

function update_{{model_name}}(csrf_token, {{model_name}}_pk, params, success_handler, failure_handler)
{
    var url = "/{{app_label}}/{{model_name}}/update/" + {{model_name}}_pk + "/";
    ajax_call(csrf_token, url, params, success_handler, failure_handler);
}

function delete_{{model_name}}(csrf_token, {{model_name}}_pk, success_handler, failure_handler)
{
    var url = "/{{app_label}}/{{model_name}}/delete/" + {{model_name}}_pk + "/";
    var params = {'delete': 1, 'pk': {{model_name}}_pk};
    ajax_call(csrf_token, url, params, success_handler, failure_handler);
}

function _{{model_name}}Api(csrf_token)
{
    var self = this;
    this.csrf_token = csrf_token;

    if(typeof(this.view_model)=='undefined')
    {
        _{{model_name}}Api.prototype.view_model = function({% for field, values in field_names.items %}{% if field == model_name %}{% for f in values %}{% if not forloop.first %}, {% endif %}{{f}}{% endfor %}{% endif %}{% endfor %}) {
            return function ViewModel({% for field, values in field_names.items %}{% if field == model_name %}{% for f in values %}{% if not forloop.first %}, {% endif %}{{f}}{% endfor %}{% endif %}{% endfor %})
            {
            {% for field, values in field_names.items %}{% if field == model_name %}{% for f in values %}
                this.{{f}} = ko.observable({{f|safe}});{% endfor %}{% endif %}{% endfor %}
            }
        }
    }

    if(typeof(this.get_fields)=='undefined')
    {
        _{{model_name}}Api.prototype.get_fields = function(){
            return {{% for field, values in field_names.items %}{% if field == model_name %}{% for f in values %}
                '{{f}}' : undefined,{% endfor %}{% endif %}{% endfor %}
            }
        };
    }

    if(typeof(this.list)=='undefined')
    {
        _{{model_name}}Api.prototype.list = function(page, success_handler, failure_handler){
            list_{{model_name}}(this.csrf_token, page, success_handler, failure_handler);
        };
    }

    if(typeof(this.get)=='undefined')
    {
        _{{model_name}}Api.prototype.get = function(pk, success_handler, failure_handler){
            get_{{model_name}}(this.csrf_token, pk, success_handler, failure_handler);
        };
    }

    if(typeof(this.add)=='undefined')
    {
        _{{model_name}}Api.prototype.add = function(params, success_handler, failure_handler){
            add_{{model_name}}(this.csrf_token, params, success_handler, failure_handler);
        };
    }

    if(typeof(this.update)=='undefined')
    {
        _{{model_name}}Api.prototype.update = function(pk, params, success_handler, failure_handler){
            update_{{model_name}}(this.csrf_token, pk, params, success_handler, failure_handler);
        };
    }

    if(typeof(this.delete)=='undefined')
    {
        _{{model_name}}Api.prototype.delete = function(pk, success_handler, failure_handler){
            delete_{{model_name}}(this.csrf_token, pk, success_handler, failure_handler);
        };
    }

    {% for ajax_view in ajax_views %}
    if(typeof(this.{{ajax_view}})=='undefined')
    {
        _{{model_name}}Api.prototype.{{ajax_view}} = function(params, success_handler, failure_handler){
            ajax_call(this.csrf_token, '/api/{{app_label}}/{{model_name}}/{{ajax_view}}/', params, success_handler, failure_handler);
        };
    }
    {% endfor %}
}


var {{model_name}}_view_model = function(params)
    {{% for field, values in field_names.items %}{% if field == model_name %}{% for f in values %}
        this.{{f}} = ko.observable(params['{{f|safe}}']);{% endfor %}{% endif %}{% endfor %}
    }


function get_{{model_name}}_view_model(pk, callback)
{
    {{model_name}}Api.get(pk, function(data) { callback(new {{model_name}}_view_model(data))});
}


function get_{{model_name}}_view_array(callback, page)
{
    {{model_name}}Api.list(page, function(data){
        var result = new Array();
        $.each(data['object_list'], function(index, value) {
            result.push(new {{model_name}}_view_model(value));
        });

        callback(result);
    });
}

{% endfor %}