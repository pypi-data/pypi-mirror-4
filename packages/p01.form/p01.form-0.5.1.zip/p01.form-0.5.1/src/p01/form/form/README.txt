======
README
======

This package re-defines the form layout normaly used from z3c.formui and also
enhances the widget within a layout concept known from our pagelets. This means
we moved some HTML rendering parts, normaly defined in a form, to the widget.
This allows us to render different HTML per widget which is not possible with
the default z3c.form and z3c.formui concepts. Because this concepts are to 
generic if it comes to render a specific widget for a form. We can now use
different widget layouts for different forms without to reimplement the widget
template. We simply can define a new widget layout for a special forms. As you
can see below, we also support more specific CSS wrapper classes depending on
the widget type (based on widget.style).

NOTE; the additional/optional layout concept just works if you call the widget.
Normaly you whould just render the widget and everyting works as usual:

  <tal:block define="widget nocall:view/widgets/email">
    <div metal:use-macro="macro:widget-row" />
  </tal:block>

Now, you can simply call the widget and the layout also get invoked e.g.:

  <tal:block replace="structure view/widgets/email"></tal:block>

We developed this with twitter bootstrap in mind. This means the concept is
compatible with twitter bootstrap but doesn't implement the bootstrap styles
out of the box. But you can simply define a form and some widget templates
for support the bootstrap styles.


structure
---------

The z3c.formui HTML structure looks like:

  <!-- original z3c.formui css classes -->
  <form>
    <div class="row">
      <div class="label">
        <label>
          <span class="label"></span>
          <span class="required"></span>
        </label>
      </div>
      <div class="widget">
        <input />
      </div>
      <div class="errors">
        <div class="error"></div>
      </div>
    </div>
  </form>

Your new HTML structure will look like (see '<--' comments):

  <!-- p01.form -->
  <div class="span4">                          <-- size wrapper
    <div class="group|inline widgets">           <-- layout wrapper
      ...
      <!-- widget -->
      <div class="text-error text" id="*-row"> <-- widget wrapper (optional prefix *-error)
        <label>                                <-- label
          <span class="label"></span>
          <span class="required"></span>
        </label>
        <div class="widget">                   <-- widget wrapper
          <input />                            <-- widget
        </div>
        <div class="errors">                   <-- error wrapper
          <div class="error"></div>            <-- error messages
        </div>
      </div>
      ...
    </div>
  </div>

This allows us to define each level of widget rendering in CSS. Here are some
samples:

  form .span4 .radio input {
      padding-left: 0;
      margin-bottom: 0;
      vertical-align: middle;
  }

Of corse we could also use CSS selectors like ``input[type="radio"]``. But we
can't add a widget background image on our ``<div class="text"></div>``
depending on ``input[type="text"]`` because the <div> tag which needs a
background-image is above our input element.

  form .span4 .text {
      width: 300px;
      padding: 1px 0px 1px 0x;
      background: url(../img/bg-input-300px.png) no-repeat;
  }

  form .span4 .text input {
      width: 296px;
      border: 0;
  }


IMPORTANT
---------

If you use the form template out of the box, you need to rename the row class
in all bootstrap *.less files to something else e.g. "rows" because the
z3c.form and p01.form framework also uses the "row" class as a widget wrapper.
See form.pt form information.

But if you don't use the form as a generic template like we do in our projects,
then you can simply define your one widget structure. Here is a sample how we
define our form templates:

  <form action="." method="post" enctype="multipart/form-data" class="form"
        tal:attributes="action view/action;
                        name view/name;
                        id view/id"
        i18n:domain="p01">
    <div class="group" tal:content="structure view/widgets/firstName"></div>
    <div class="group" tal:content="structure view/widgets/lastName"></div>
    <div class="group" tal:content="structure view/widgets/street"></div>
    <div class="group" tal:content="structure view/widgets/zip"></div>
    <div class="group" tal:content="structure view/widgets/city"></div>
    <div metal:use-macro="macro:header"></div>
    <div class="btns">
      <div class="left">
        <input tal:replace="structure view/actions/doApplyComment/render|nothing" />
      </div>
      <div class="right">
        <input tal:replace="structure view/actions/close/render|nothing" />
      </div>
    </div>
  </form>

In the sample above, you can see that we use "group" as the widget wrapper
class name and not "row" as the default form.pt template offers.
