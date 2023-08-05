======
README
======


LoremIpsumTextGenerator
-----------------------

This is a lorem ipsum text generator which can generate lorem ipsum text lines.

  >>> from p01.sampledata.generator import LoremIpsumGenerator
  >>> seed = 'sample'
  >>> generator = LoremIpsumGenerator(seed)

Now we can get lorem ipsum text:

  >>> print generator.get()
  Pellentesque lacinia suscipit nisi. Ut convallis orci sit amet eros viverra
  fermentum. Quisque velit tellus, sodales scelerisque, dignissim non, suscipit
  sit amet, sem. Class aptent taciti sociosqu ad litora torquent per conubia
  nostra, per inceptos hymenaeos. In hac habitasse platea dictumst. Proin risus.
  Donec dapibus facilisis eros. Aliquam vel magna semper massa laoreet
  imperdiet. Aliquam cursus malesuada justo. Sed eu quam. Nunc faucibus dui
  quis felis. Curabitur cursus dapibus est. Phasellus iaculis purus at odio.
  Curabitur est justo, cursus sed, euismod a, pharetra eu, enim.

We can also get many text lines:

  >>> generator.getMany(2)
  [u'Nunc feugiat tincidunt est. Ut venenatis viverra nisi. Pellentesque nec
     felis. Duis porttitor, ligula fringilla pretium consequat, turpis tortor
     nonummy tortor, eu pretium augue tortor vel ante. Suspendisse vitae justo
     ac eros bibendum laoreet. Proin ut neque. Duis imperdiet facilisis leo.
     Nullam molestie sapien id velit. Curabitur commodo ultricies metus. Nulla a
     urna. Sed ultrices rutrum diam. Nulla sollicitudin mollis purus. Etiam
     sodales semper urna. Cras et eros. Fusce risus. Nam pharetra turpis id nunc.
     Donec sit amet ipsum. Aliquam feugiat, est quis mattis nonummy, erat tortor
     aliquet mi, ut facilisis tortor lacus non metus.',
   u'Nulla facilisi. Morbi dignissim augue nec nisl. Sed sit amet felis. Etiam
     mollis. Suspendisse potenti. Nulla convallis, mauris in consectetuer
     posuere, eros purus tempus lorem, sed vulputate pede purus quis leo.
     Phasellus semper, arcu et ultricies elementum, felis magna lacinia ipsum,
     a porttitor tortor purus eget erat. Quisque orci lectus, sagittis quis,
     tristique quis, iaculis ac, arcu. Integer fringilla, turpis id euismod
     consectetuer, magna neque auctor arcu, nec eleifend nulla sapien ut justo.
     Nullam pede justo, interdum fringilla, rutrum ut, dapibus eu, nulla.']