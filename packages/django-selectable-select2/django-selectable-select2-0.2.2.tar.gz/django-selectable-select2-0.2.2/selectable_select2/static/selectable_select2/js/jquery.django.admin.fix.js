/**
    This is a hot fix for including 3rd party JS plugins into the django admin.
    I'm no Javascript expert and if this may lead to any bugs or confusion let me know.
*/

if (typeof(django) != 'undefined' && typeof(django.jQuery) != 'undefined' && typeof(jQuery) == 'undefined') {
    jQuery = django.jQuery;
}
else {

}
