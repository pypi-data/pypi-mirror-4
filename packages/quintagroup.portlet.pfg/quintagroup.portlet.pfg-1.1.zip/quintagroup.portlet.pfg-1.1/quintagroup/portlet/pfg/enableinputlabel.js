jq(document).ready(function() {
    jq('.portletPFG .ArchetypesStringWidget').each(function(){jq('input',this).attr('title',jq('label',this).text()).addClass('inputLabel')})
});
