Introduction
============

This Plone-add-on supplies a fullscreen-button 
below the title of any plone article, symbolized with expanding
and collapsing arrows.

The button consists of four unicode-arrow-characters, so can easily
obtain visual control over the element via, f.e. change color, include 
a background-image, or such.

When clicked, left- and right-columns and top- and footer-elements are 
hidden and the main column expands to full width and height of the window.

On reload or calling another page, the view falls back to non-fullscreen 
in order to not accidently hide releveant context information, if the 
user forgets being in fullscreenmode.

Please note, that the term 'fullscreen' here doesn't mean, the browserwindow 
dissapears, but any element but the actual article is hidden, which let's 
you focus more on the content. For the former you can also just user the 
fulscreenmode of your browser, conventionally accessible via the F11-key.
