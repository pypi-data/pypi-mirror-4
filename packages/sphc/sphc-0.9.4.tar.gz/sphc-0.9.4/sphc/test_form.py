import sphc.more

form = sphc.more.Form()

about = form.add(sphc.more.Fieldset())
about.add(sphc.tf.LEGEND('About'))
about.add_field('Name', sphc.tf.INPUT(name='name', type='text'))

contact = sphc.more.Fieldset()
contact.add(sphc.tf.LEGEND('About'))
contact.add_field('Name', sphc.tf.INPUT(name='name', type='text'))

form.add(about)
form.add(contact)
#form.add_buttons(...)

print(form.build())
