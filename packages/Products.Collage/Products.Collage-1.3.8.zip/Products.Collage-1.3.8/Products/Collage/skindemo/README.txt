#####################
Collage skinning demo
#####################

Enable this skinning demo near the end of the main configure.zcml that
comes with this Product.

In ZMI, add manually to the portal_css the following stylesheet (yup,
I'm too lazy to make a GS profile only for this ;o):

  Id: ++resource++collage-skindemo-stylesheets/alert.css
  CSS Media: all
  Condition: object/@@collage|nothing

Leave the default values to the other fields.

Check the Debug mode of portal_css.

Go to any collage object, set the model of any component to "portlet",
then select "alert portlet skin" in the "skins" section. That's it.
