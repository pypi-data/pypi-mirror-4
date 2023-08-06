(function($) {
    $(document).ready(function($) {

        $('td.field-unit_price input').keyup(function() {
            p = (this.id);
            n = p.indexOf("-");
            t = p.indexOf("-unit_price");
            c = p.substring(n+1, t);
            if ($('#id_line-'+c+'-quantity').val().length > 0 && isNaN($('#id_line-'+c+'-quantity').val()) == false) {
              res = $('#id_line-'+c+'-quantity').val() * $('#id_line-'+c+'-unit_price').val()
              $('#id_line-'+c+'-amount').val(res);
            }
        });

    });
})(django.jQuery);