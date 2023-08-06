/* collapsing for tagNavigator */

var TagNav = {};

TagNav.getCollapseValue = function ()
{
    if(jq('.tagNavigator')[0])
    {
        var cl = jq('.tagNavigator').attr('class');
        return parseInt(cl.substring(cl.length-1,cl.length));
    }
    return 0;
};

TagNav.collapse = function (ob)
{
    var state = jq(ob).css('display');
    
    if (state == "none")
    {
        jq(ob).css('display', 'block');
    }
    else
    {
        jq(ob).css('display', 'none');
    }
};

TagNav.switchIcon = function (ob)
{
    var text = jq(ob).text();
    var icon = text.substring(0,1);
    if(icon == "+")
    {
        icon = "-";
    }
    else
    {
        icon = "+";
    }
    
    jq(ob).text(icon + text.substring(1, text.length));
};

TagNav.openSelected = function ()
{
        jq('.nc-category_selected').parents('ul').siblings('.cn-category-title').click();
}

TagNav.setup = function ()
{
    if(TagNav.getCollapseValue() == 2)
    {
        jq("ul.subcategory .cn-category-title").click(function () {
                jq(this).siblings('ul').each(function()
                    {
                        TagNav.collapse(jq(this))
                    });
                TagNav.switchIcon(jq(this));
            });
    }
    else
    {
    }
    
    TagNav.openSelected();
};

jq(document).ready(TagNav.setup);