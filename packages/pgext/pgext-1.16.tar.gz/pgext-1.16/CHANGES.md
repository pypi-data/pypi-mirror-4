Release 1.16

 * fixed Ubuntu compilation errors
 * minor code improvements, code cleaning
 * filters.ripple - another useless visual effect :)
 * code examples (in examples folder): hue, noise, ripple, noiseBlur, pixelize


Release 1.15

 * faster filters.noise function
 * fixed memleak - wrong usage of Py_INCREF (not needed for PySurface_New)

Release 1.14

 * 24bit(RGB) input surface support
 * C code improvements
 * windows bin package and installer available for download
 * improved documentation & demo images
 * color.alphaMask now returns new surface instead of modifing input surface

Release 1.13

 * filters.pixelize - fixed pixels source
 * filters.pixelize - fixed memory leak
 * fixed MSVC9 compile errors

Release 1.12

 * NEW - filters.pixelize
 * minor improvements

Release 1.11

 * NEW - color.multiply
 * NEW - filters.noiseBlur
 * blur, hvBlur - optimization; fixed surface edge blur
 * optimization

Release 1.10

 * color.alphaMask - method attribute (use mask.value or mask.alpha)
 * filters.gradient - RGBA gradients

Release 1.9

 * NEW - filters.scratch
 * filters.shadow - fixed target/source surface format
 * deform module removed
 * new testing image - Lena
 * C code refactoring
 * documentation refactoring

Release 1.8

 * New documentation

Release 1.7

 * NEW - color.alphaMask
 * NEW - color.hue
 * NEW - color.lightness
 * minor improvements

Release 1.5

 * Improved setup/config script
 * Windows/MSVC support
