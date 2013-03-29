%define poppler_version 0.11.0
%define glib2_version 2.18.0
%define gtk2_version 2.14.0
%define dbus_version 0.70
%define theme_version 2.17.1

Name:		evince
Version:	2.28.2
Release:	14%{?dist}.1
Summary:	Document viewer

License:	GPLv2+ and GFDL
Group:		Applications/Publishing
URL:		http://projects.gnome.org/evince/
Source0:	http://download.gnome.org/sources/%{name}/2.28/%{name}-%{version}.tar.bz2
Obsoletes:	evince-djvu <= 2.28.2

# https://bugzilla.gnome.org/show_bug.cgi?id=596888
Patch1:		0001-Provide-some-indication-that-search-is-not-available.patch
Patch2:		evince-thumbnail-allocation.patch
# http://bugzilla.gnome.org/613637
Patch3:		evince-dir-prefix.patch

# make docs show up in rarian/yelp
Patch4:         evince-doc-category.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=589191
Patch5:         evince-translation.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=591051
Patch6:         evince-relative-path.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=591132
Patch7:         evince-zoom.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=592963
Patch8:         evince-disable-rotated-selection.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=591087
Patch9:         evince-autorotate-scale.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=600693
Patch10:        evince-default-page-scale.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=589191
Patch11:         evince-translation2.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=666323
Patch12:	evince-CVE-2010-2640_CVE-2010-2641_CVE-2010-2642_CVE-2010-2643.patch

BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:	gtk2-devel >= %{gtk2_version}
BuildRequires:	glib2-devel >= %{glib2_version}
BuildRequires:	poppler-glib-devel >= %{poppler_version}
BuildRequires:	libXt-devel
BuildRequires:	nautilus-devel
BuildRequires:	gnome-keyring-devel
BuildRequires:	libglade2-devel
BuildRequires:	libtiff-devel
BuildRequires:	libjpeg-devel
BuildRequires:	libspectre-devel
BuildRequires:	gnome-doc-utils
BuildRequires:	scrollkeeper
BuildRequires:	dbus-glib-devel >= %{dbus_version}
BuildRequires:	gettext
BuildRequires:	desktop-file-utils
BuildRequires:	gnome-icon-theme >= %{theme_version}
BuildRequires:	libtool
BuildRequires:	gtk-doc
BuildRequires:	intltool
BuildRequires:	GConf2-devel

# for the dvi backend
BuildRequires: kpathsea-devel

# for /etc/gconf/schemas
Requires: GConf2

Requires(pre): GConf2
Requires(post): GConf2
Requires(post): scrollkeeper
Requires(preun): GConf2
Requires(postun): scrollkeeper
Requires: %{name}-libs = %{version}-%{release}

%description
Evince is simple multi-page document viewer. It can display and print
Portable Document Format (PDF), PostScript (PS) and Encapsulated PostScript
(EPS) files. When supported by the document format, evince allows searching
for text, copying text to the clipboard, hypertext navigation,
table-of-contents bookmarks and editing of forms.

Support for other document formats such as DVI can be added by installing
additional backends.


%package libs
Summary: Libraries for the evince document viewer
Group: System Environment/Libraries

%description libs
This package contains shared libraries needed for evince 


%package devel
Summary: Support for developing backends for the evince document viewer
Group: Development/Libraries
Requires: %{name}-libs = %{version}-%{release}

%description devel
This package contains libraries and header files needed for evince
backend development.


%package dvi
Summary: Evince backend for dvi files
Group: Applications/Publishing
Requires: %{name}-libs = %{version}-%{release}

%description dvi
This package contains a backend to let evince display dvi files.


%prep
%setup -q
%patch1 -p1 -b .search-not-available
%patch2 -p0 -b .thumbnail-allocation
%patch3 -p1 -b .dir-prefix
%patch4 -p1 -b .doc-category
%patch5 -p1 -b .translation
%patch6 -p1 -b .relative-path
%patch7 -p1 -b .zoom
%patch8 -p1 -b .disable-rotated-selection
%patch9 -p1 -b .autorotate-scale
%patch10 -p1 -b .default-scale
%patch11 -p1 -b .translation2
%patch12 -p1 -b .CVE-2010-2640_CVE-2010-2641_CVE-2010-2642_CVE-2010-2643

%build
%configure --disable-static --disable-scrollkeeper \
	--with-platform=gnome \
	--enable-comics=yes \
	--enable-dvi=yes \
	--disable-djvu
make %{?_smp_mflags} LIBTOOL=/usr/bin/libtool

%install
rm -rf $RPM_BUILD_ROOT
export GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL=1
make install DESTDIR=$RPM_BUILD_ROOT

desktop-file-install --delete-original --vendor="" \
  --dir=$RPM_BUILD_ROOT%{_datadir}/applications \
  --remove-category="Application" \
  $RPM_BUILD_ROOT%{_datadir}/applications/evince.desktop

%find_lang evince --with-gnome

unset GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL

mkdir -p $RPM_BUILD_ROOT%{_datadir}/applications
/bin/rm -rf $RPM_BUILD_ROOT/var/scrollkeeper
# Get rid of static libs and .la files.
rm -f $RPM_BUILD_ROOT%{_libdir}/nautilus/extensions-2.0/*.la
rm -f $RPM_BUILD_ROOT%{_libdir}/nautilus/extensions-2.0/*.a
rm -f $RPM_BUILD_ROOT%{_libdir}/evince/1/backends/*.la
rm -f $RPM_BUILD_ROOT%{_libdir}/evince/1/backends/*.a
rm -f $RPM_BUILD_ROOT%{_libdir}/*.la
rm -f $RPM_BUILD_ROOT%{_libdir}/*.a

# don't ship icon caches
rm -f $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/icon-theme.cache

%clean
rm -rf $RPM_BUILD_ROOT


%pre
if [ "$1" -gt 1 ]; then
	export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
	gconftool-2 --makefile-uninstall-rule \
		%{_sysconfdir}/gconf/schemas/evince.schemas \
		%{_sysconfdir}/gconf/schemas/evince-thumbnailer.schemas \
		%{_sysconfdir}/gconf/schemas/evince-thumbnailer-comics.schemas \
			>/dev/null || :
	if [ -f %{_sysconfdir}/gconf/schemas/evince-thumbnailer-dvi.schemas ]; then
		gconftool-2 --makefile-uninstall-rule \
			%{_sysconfdir}/gconf/schemas/evince-thumbnailer-dvi.schemas \
			>/dev/null || :
	fi
fi


%post
export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
gconftool-2 --makefile-install-rule \
	%{_sysconfdir}/gconf/schemas/evince.schemas \
	%{_sysconfdir}/gconf/schemas/evince-thumbnailer.schemas \
	%{_sysconfdir}/gconf/schemas/evince-thumbnailer-ps.schemas \
	%{_sysconfdir}/gconf/schemas/evince-thumbnailer-comics.schemas \
	%{_sysconfdir}/gconf/schemas/evince-thumbnailer-dvi.schemas \
		>/dev/null || :

update-desktop-database &> /dev/null ||:
scrollkeeper-update -q -o %{_datadir}/omf/%{name} || :

touch --no-create %{_datadir}/icons/hicolor
if [ -x /usr/bin/gtk-update-icon-cache ]; then
  /usr/bin/gtk-update-icon-cache -q %{_datadir}/icons/hicolor;
fi

%post libs -p /sbin/ldconfig

%preun
if [ "$1" -eq 0 ]; then
	export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
	gconftool-2 --makefile-uninstall-rule \
		%{_sysconfdir}/gconf/schemas/evince.schemas \
		%{_sysconfdir}/gconf/schemas/evince-thumbnailer.schemas \
		%{_sysconfdir}/gconf/schemas/evince-thumbnailer-ps.schemas \
		%{_sysconfdir}/gconf/schemas/evince-thumbnailer-comics.schemas \
		%{_sysconfdir}/gconf/schemas/evince-thumbnailer-dvi.schemas \
			>/dev/null || :
fi


%postun
update-desktop-database &> /dev/null ||:
scrollkeeper-update -q || :

touch --no-create %{_datadir}/icons/hicolor
if [ -x /usr/bin/gtk-update-icon-cache ]; then
  /usr/bin/gtk-update-icon-cache -q %{_datadir}/icons/hicolor;
fi

%postun libs -p /sbin/ldconfig

%files -f evince.lang
%defattr(-,root,root,-)
%doc README COPYING NEWS AUTHORS
%{_bindir}/*
%{_libdir}/nautilus/extensions-2.0/libevince-properties-page.so
%{_datadir}/%{name}/
%{_datadir}/applications/%{name}.desktop
%{_sysconfdir}/gconf/schemas/*.schemas
%{_datadir}/icons/hicolor/*/apps/evince.*
%{_mandir}/man1/evince.1.gz

%files libs
%defattr(-,root,root,-)
%{_libdir}/libevview.so.*
%{_libdir}/libevdocument.so.*
%dir %{_libdir}/evince
%dir %{_libdir}/evince/1
%dir %{_libdir}/evince/1/backends
%{_libdir}/evince/1/backends/libpdfdocument.so
%{_libdir}/evince/1/backends/pdfdocument.evince-backend
%{_libdir}/evince/1/backends/libpsdocument.so
%{_libdir}/evince/1/backends/psdocument.evince-backend
%{_libdir}/evince/1/backends/libtiffdocument.so
%{_libdir}/evince/1/backends/tiffdocument.evince-backend
%{_libdir}/evince/1/backends/libcomicsdocument.so
%{_libdir}/evince/1/backends/comicsdocument.evince-backend

%files devel
%defattr(-,root,root,-)
%{_datadir}/gtk-doc/html/evince/
%{_datadir}/gtk-doc/html/libevdocument/
%{_datadir}/gtk-doc/html/libevview/
%dir %{_includedir}/evince
%{_includedir}/evince/2.25
%{_libdir}/libevview.so
%{_libdir}/libevdocument.so
%{_libdir}/pkgconfig/evince-view-2.25.pc
%{_libdir}/pkgconfig/evince-document-2.25.pc

%files dvi
%defattr(-,root,root,-)
%{_libdir}/evince/1/backends/libdvidocument.so*
%{_libdir}/evince/1/backends/dvidocument.evince-backend

%changelog
* Mon Jan  3 2011 Marek Kasik <mkasik@redhat.com> - 2.28.2-14.el6_0.1
- Fixes CVE-2010-2640, CVE-2010-2641, CVE-2010-2642 and CVE-2010-2643
- Resolves: #666323

* Mon Aug  9 2010 Marek Kasik <mkasik@redhat.com> - 2.28.2-14
- Update translations
- patch by Ankit Patel
- Resolves: #589191

* Tue Jun 22 2010 Marek Kasik <mkasik@redhat.com> - 2.28.2-13
- Change default page scaling to "Shrink to Printable Area"
- Resolves: #600693

* Fri May 21 2010 Marek Kasik <mkasik@redhat.com> - 2.28.2-12
- Add controls for scaling and autorotating pages when printing
- Resolves: #591087

* Mon May 17 2010 Marek Kasik <mkasik@redhat.com> - 2.28.2-11
- Disable text selection if document is rotated
- Resolves: #592963

* Mon May 17 2010 Marek Kasik <mkasik@redhat.com> - 2.28.2-10
- Fix check for maximal and minimal zoom
- Resolves: #591132

* Wed May 12 2010 Marek Kasik <mkasik@redhat.com> - 2.28.2-9
- Convert relative path to correct URI for evince-previewer
- Resolves: #591051

* Thu May  6 2010 Marek Kasik <mkasik@redhat.com> - 2.28.2-8
- Update translations
- Resolves: #589191

* Mon May  3 2010 Matthias Clasen <mclasen@redhat.com> 2.28.2-7
- Make docs show up in yelp
- Resolves: #588536

* Mon Mar 22 2010 Ray Strode <rstrode@redhat.com> 2.28.2-6
- Support relocatable .gnome2
- Resolves: #575934

* Wed Mar  3 2010 Marek Kasik <mkasik@redhat.com> - 2.28.2-5
- Obsolete evince-djvu
- Resolves: #570095

* Tue Feb  9 2010 Marek Kasik <mkasik@redhat.com> - 2.28.2-4
- Remove DjVu backend.
- Resolves: #562821

* Thu Jan  7 2010 Marek Kasik <mkasik@redhat.com> - 2.28.2-3
- Really remove unused patches
- Related: #543948

* Thu Jan  7 2010 Marek Kasik <mkasik@redhat.com> - 2.28.2-2
- Don't use RPATH
- Remove static libs
- Remove unused patches
- Fix mixed use of spaces and tabs in spec file
- Avoid expansion of some macros in changelog
- Related: #543948

* Mon Jan  4 2010 Matthias Clasen <mclasen@redhat.com> - 2.28.2-1
- Update to 2.28.2

* Thu Oct 29 2009 Marek Kasik <mkasik@redhat.com> - 2.28.1-5
- Add backported patch evince-aspect-ratio.patch (#531430).
- Preserve aspect ratio of scaled pages and set page orientation
- automatically (gnome bugs #599468 and #599470)

* Tue Oct 27 2009 Matthias Clasen <mclasen@redhat.com> - 2.28.1-4
- Avoid a help file seriesid clash

* Thu Oct 22 2009 Marek Kasik <mkasik@redhat.com> - 2.28.1-3
- Add evince-thumbnail-allocation.patch (checks whether
- GdkPixbuf was allocated correctly)

* Thu Oct 22 2009 Matthias Clasen <mclasen@redhat.com> - 2.28.1-2
- Provide some hint if search is not available

* Tue Oct 20 2009 Marek Kasik <mkasik@redhat.com> - 2.28.1-1
- Update to 2.28.1
- Add evince-pdf-print-revert.patch (reverts upstream's change
- of print which revealed the bug #517310)

* Mon Sep 21 2009 Matthias Clasen <mclasen@redhat.com> - 2.28.0-1
- Update to 2.28.0

* Tue Aug 11 2009 Matthias Clasen <mclasen@redhat.com> - 2.27.90-1
- Update to 2.27.90

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.27.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Jul 13 2009 Matthias Clasen <mclasen@redhat.com> - 2.27.4-1
- Update to 2.27.4

* Tue Jun 16 2009 Matthias Clasen <mclasen@redhat.com> - 2.27.3-1
- Update to 2.27.3

* Sat May 23 2009 Michael Schwendt <mschwendt@fedoraproject.org> - 2.27.1-2
- Include /usr/include/evince directory (#483306).
- Don't run /sbin/ldconfig in post scriptlet (no shared libs in that pkg).
- Let -libs post/postun run /sbin/ldconfig directly.

* Tue May 19 2009 Bastien Nocera <bnocera@redhat.com> 2.27.1-1
- Update to 2.27.1

* Fri May 01 2009 Peter Robinson <pbrobinson@gmail.com> - 2.26.1-1
- Update to 2.26.1

* Fri May 01 2009 Peter Robinson <pbrobinson@gmail.com> - 2.26.0-2
- Split libs out to a subpackage - RHBZ 480729

* Mon Mar 16 2009 Matthias Clasen  <mclasen@redhat.com> - 2.26.0-1
- Update to 2.26.0

* Mon Mar  2 2009 Matthias Clasen  <mclasen@redhat.com> - 2.25.92-1
- Update to 2.25.92

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.25.91-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Tue Feb 17 2009 Matthias Clasen  <mclasen@redhat.com> - 2.25.91-1
- Update to 2.25.91

* Tue Feb  3 2009 Matthias Clasen  <mclasen@redhat.com> - 2.25.90-1
- Update to 2.25.90

* Tue Jan 20 2009 Matthias Clasen  <mclasen@redhat.com> - 2.25.5-1
- Update to 2.25.5

* Sat Jan 17 2009 Rakesh Pandit <rakesh@fedoraproject.org> - 2.25.4-2
- Rebuild with mew djvulibre

* Mon Jan  5 2009 Matthias Clasen  <mclasen@redhat.com> - 2.25.4-1
- Update to 2.25.4
- Temporarily drop the duplex patch, it needs updating

* Wed Dec  3 2008 Matthias Clasen  <mclasen@redhat.com> - 2.25.2-2
- Update to 2.25.2

* Fri Nov 21 2008 Matthias Clasen  <mclasen@redhat.com> - 2.25.1-5
- Better URL

* Fri Nov 21 2008 Matthias Clasen  <mclasen@redhat.com> - 2.25.1-4
- Tweak %%summary and %%description

* Tue Nov 11 2008 Matthias Clasen  <mclasen@redhat.com> - 2.25.1-3
- Update to 2.25.1

* Sat Oct 25 2008 Matthias Clasen  <mclasen@redhat.com> - 2.24.1-3
- Require dbus-glib-devel, not just dbus-devel (#465281, Dan Winship)

* Sat Oct 25 2008 Ville Skyttä <ville.skytta at iki.fi> - 2.24.1-2
- Drop dependency on desktop-file-utils (#463048).

* Mon Oct 20 2008 Matthias Clasen  <mclasen@redhat.com> - 2.24.1-1
- Update to 2.24.1

* Mon Sep 22 2008 Matthias Clasen  <mclasen@redhat.com> - 2.24.0-1
- Update to 2.24.0

* Fri Sep  12 2008 Marek Kasik <mkasik@redhat.com> - 2.23.92-2
- fix duplex printing of copies
- upstream bug #455759

* Tue Sep  9 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.92-1
- Update to 2.23.92

* Tue Sep  2 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.91-1
- Update to 2.23.91

* Thu Aug 28 2008 Michael Schwendt <mschwendt@fedoraproject.org> - 2.23.6-2
- Include %%_libdir/evince directory.

* Wed Aug  6 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.6-1
- Update to 2.23.6

* Tue Jul 22 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.5-1
- Update to 2.23.5

* Thu Jul 17 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 2.23.4-2
- fix license tag

* Wed Jun 18 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.4-1
- Update to 2.23.4

* Tue Apr  8 2008 Matthias Clasen <mclasen@redhat.com> - 2.22.1.1-1
- Update to 2.22.1.1 (fix link handling in djvu backend)

* Mon Apr  7 2008 Matthias Clasen <mclasen@redhat.com> - 2.22.1-1
- Update to 2.22.1

* Tue Apr  1 2008 Kristian Høgsberg <krh@redhat.com> - 2.22.0-4
- Rebuild against latest poppler.

* Mon Mar 17 2008 Matthias Clasen <mclasen@redhat.com> - 2.22.0-3
- Handle all schemas files

* Thu Mar 13 2008 Matthias Clasen <mclasen@redhat.com> - 2.22.0-2
- Rebuild against the latest poppler

* Mon Mar 10 2008 Matthias Clasen <mclasen@redhat.com> - 2.22.0-1
- Update to 2.22.0

* Mon Mar  3 2008 Matthias Clasen <mclasen@redhat.com> - 2.21.91-2
- Rebuild

* Tue Feb 12 2008 Matthias Clasen <mclasen@redhat.com> - 2.21.91-1
- Update to 2.21.91

* Sat Feb  2 2008 Matthias Clasen <mclasen@redhat.com> - 2.21.90-5
- Fix nautilus property page and thumbnailer

* Wed Jan 30 2008 Matthias Clasen <mclasen@redhat.com> - 2.21.90-4
- Use libspectre

* Wed Jan 30 2008 Matthias Clasen <mclasen@redhat.com> - 2.21.90-3
- Don't link the thumbnailer against djvu

* Mon Jan 28 2008 Matthias Clasen <mclasen@redhat.com> - 2.21.90-2
- Rebuild against split poppler

* Mon Jan 28 2008 Matthias Clasen <mclasen@redhat.com> - 2.21.90-1
- Update to 2.21.90

* Sun Dec 23 2007 Matthias Clasen <mclasen@redhat.com> - 2.21.1-2
- Build nautilus extension against nautilus 2.21

* Wed Dec  5 2007 Matthias Clasen <mclasen@redhat.com> - 2.21.1-1
- Update to 2.21.1

* Tue Dec  4 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.2-2
- Enable the dvi backend

* Tue Nov 27 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.2-1
- Update to 2.20.2

* Mon Nov 26 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.1-5
- Fix a problem in the tiff patch
- Turn off the dvi backend for now, since the tetex kpathsea 
  gives linker errors on x86_64

* Sat Nov 17 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.1-4
- Enable the dvi and djvu backends

* Thu Nov 15 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.1-3
- Fix rendering of tiff images (#385671)

* Tue Oct 23 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.1-2
- Rebuild against new dbus-glib

* Mon Oct 15 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.1-1
- Update to 2.20.1 (bug fixes and translation updates)

* Wed Oct  3 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.0-3
- Drop the nautilus dependency (#201967)

* Mon Sep 24 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.0-2
- Add a missing schema file

* Mon Sep 17 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.0-1
- Update to 2.20.0

* Tue Sep  4 2007 Kristian Høgsberg <krh@redhat.com> - 2.19.92-1
- Update to 2.19.92.  Evince now follows GNOME version numbers.

* Wed Aug 15 2007 Matthias Clasen <mclasen@redhat.com> - 0.9.3-5
- Rebuild

* Sat Aug 11 2007 Matthias Clasen <mclasen@redhat.com> - 0.9.3-4
- Fix the build

* Mon Aug  6 2007 Matthias Clasen <mclasen@redhat.com> - 0.9.3-3
- Update licence field again
- Use %%find_lang for help files, too
- Add some missing requires

* Thu Aug  2 2007 Matthias Clasen <mclasen@redhat.com> - 0.9.3-2
- Update the license field

* Mon Jul 30 2007 Matthias Clasen <mclasen@redhat.com> - 0.9.3-1
- Update to 0.9.3

* Tue Jul 10 2007 Matthias Clasen <mclasen@redhat.com> - 0.9.2-1
- Update to 0.9.2

* Mon Jun 18 2007 Matthias Clasen <mclasen@redhat.com> - 0.9.1-1
- Update to 0.9.1

* Mon Jun 11 2007 - Bastien Nocera <bnocera@redhat.com> - 0.9.0-3
- Add comics-related build fixes

* Mon Jun 11 2007 - Bastien Nocera <bnocera@redhat.com> - 0.9.0-2
- Enable comics support (#186865)

* Sat May 19 2007 Matthias Clasen <mclasen@redhat.com> - 0.9.0-1
- Update to 0.9.0

* Tue Apr  3 2007 Matthias Clasen <mclasen@redhat.com> - 0.8.0-5
- Add an explicit --vendor="", to pacify older desktop-file-utils

* Sun Apr  1 2007 Matthias Clasen <mclasen@redhat.com> - 0.8.0-4
- Add an explicit BR for gnome-icon-theme (#234780)

* Sun Apr  1 2007 Matthias Clasen <mclasen@redhat.com> - 0.8.0-3
- Add an explicit --with-print=gtk to configure 
- Drop libgnomeprintui22 BR

* Sat Mar 31 2007 Matthias Clasen <mclasen@redhat.com> - 0.8.0-2
- Add support for xdg-user-dirs

* Tue Mar 13 2007 Matthias Clasen <mclasen@redhat.com> - 0.8.0-1
- Update to 0.8.0
- Use desktop-file-install

* Tue Feb 13 2007 Matthias Clasen <mclasen@redhat.com> - 0.7.2-1
- Update to 0.7.2

* Wed Jan 10 2007 Matthias Clasen <mclasen@redhat.com> - 0.7.1-1
- Update to 0.7.1

* Tue Dec 19 2006 Matthias Clasen <mclasen@redhat.com> - 0.7.0-1
- Update to 0.7.0

* Sun Dec 10 2006 Matthias Clasen <mclasen@redhat.com> - 0.6.1-2
- Fix an overflow in the PostScript backend (#217674, CVE-2006-5864)

* Fri Oct 20 2006 Matthias Clasen <mclasen@redhat.com> - 0.6.1-1
- Update to 0.6.1

* Wed Oct 18 2006 Matthias Clasen <mclasen@redhat.com> - 0.6.0-4
- Fix scripts according to the packaging guidelines
 
* Sun Oct 01 2006 Jesse Keating <jkeating@redhat.com> - 0.6.0-3.fc6
- rebuilt for unwind info generation, broken in gcc-4.1.1-21

* Fri Sep 22 2006 Matthias Clasen <mclasen@redhat.com> - 0.6.0-2.fc6
- Fix a deadlock in printing

* Mon Sep  4 2006 Matthias Clasen <mclasen@redhat.com> - 0.6.0-1.fc6
- Update to 0.6.0

* Mon Aug 21 2006 Kristian Høgsberg <krh@redhat.com> - 0.5.5-2.fc6
- Rebuild agains new dbus.

* Fri Aug 11 2006 Matthias Clasen <mclasen@redhat.com> - 0.5.5-1.fc6
- Update to 0.5.5

* Tue Jul 25 2006 Matthias Clasen <mclasen@redhat.com> - 0.5.4-3
- Don't ship an icon cache file

* Wed Jul 19 2006 Matthias Clasen <mclasen@redhat.com> - 0.5.4-2
- Rebuild against new dbus

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 0.5.4-1.1
- rebuild

* Wed Jul 12 2006 Matthias Clasen <mclasen@redhat.com> - 0.5.4-1
- Update to 0.5.4

* Thu Jun 29 2006 Kristian Høgsberg <krh@redhat.com> - 0.5.3-4
- Bump gtk2 dependency to 2.9.4.

* Thu Jun  8 2006 Matthias Clasen <mclasen@redhat.com> - 0.5.3-3
- Rebuild

* Tue May 30 2006 Kristian Høgsberg <krh@redhat.com> - 0.5.3-2
- Add gettext build requires.

* Mon May 22 2006 Kristian Høgsberg <krh@redhat.com> 0.5.3-1
- Bump poppler_version to 0.5.2.
- Package icons and add %%post and %%postun script to update icon cache.

* Wed May 17 2006 Matthias Clasen <mclasen@redhat.com> - 0.5.3-1
- Update to 0.5.3

* Tue May  9 2006 Matthias Clasen <mclasen@redhat.com> - 0.5.2-1
- update to 0.5.2

* Mon Mar  6 2006 Jeremy Katz <katzj@redhat.com> - 0.5.1-3
- quiet scriptlet spew from gconfd killing

* Wed Mar  1 2006 Kristian Høgsberg <krh@redhat.com> - 0.5.1-2
- Rebuild to pick up new poppler soname.

* Mon Feb 27 2006 Matthias Clasen <mclasen@redhat.com> - 0.5.1-1
- Update to 0.5.1
- Drop upstreamed patch

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 0.5.0-3.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 0.5.0-3.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Mon Jan 30 2006 Christopher Aillon <caillon@redhat.com> 0.5.0-3
- Don't explicitly set the invisible char to '*'

* Mon Jan 23 2006 Kristian Høgsberg <krh@redhat.com> 0.5.0-2
- Spec file update from Brian Pepple <bdpepple@ameritech.net> (#123527):
  - Drop Requires for gtk2 & poppler, devel soname pulls these in.
  - Disable GConf schema install in install section.
  - Add BR for gnome-doc-utils, nautilus & libXt-devel.
  - Use smp_mflags.
  - Drop BR for desktop-file-utils,gcc & gcc-c++.
  - Add URL & full source.
  - Use more macros.
  - Fix ownership of some directories.
  - Drop depreciated prereq, and use requires.
  - Use fedora extras preferred buildroot.
  - Various formatting changes.

* Fri Jan 20 2006 Kristian Høgsberg <krh@redhat.com> 0.5.0-1
- Update to 0.5.0 release.

* Tue Dec 13 2005 Kristian Høgsberg <krh@redhat.com> 0.4.0-4
- Added a couple of missing build requires.

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com> - 0.4.0-3.1
- rebuilt

* Thu Dec 01 2005 John (J5) Palmieri <johnp@redhat.com> - 0.4.0-3
- rebuild for new dbus

* Tue Sep 13 2005 Marco Pesenti Gritti <mpg@redhat.com> 0.4.0-2
- Rebuild

* Fri Aug 26 2005 Marco Pesenti Gritti <mpg@redhat.com> 0.4.0-1
- Update to 0.4.0
- No more need to remove ev-application-service.h

* Fri Aug 19 2005 Kristian Høgsberg <krh@redhat.com> 0.3.4-2
- Remove stale autogenerated ev-application-service.h.

* Wed Aug 17 2005 Kristian Høgsberg <krh@redhat.com> 0.3.4-1
- New upstream version again.
- Add nautilus property page .so's.
- Stop scrollkeeper from doing what it does.

* Wed Aug 17 2005 Kristian Høgsberg <krh@redhat.com> 0.3.3-2
- Bump release and rebuild.
- Require poppler > 0.4.0.

* Tue Aug 16 2005 Matthias Clasen <mclasen@redhat.com> 
- Newer upstream version

* Tue Aug 09 2005 Andrew Overholt <overholt@redhat.com> 0.3.2-3
- Add necessary build requirements.
- Bump poppler_version to 0.3.3.

* Thu Aug  4 2005 Matthias Clasen <mclasen@redhat.com> - 0.3.2-1
- Newer upstream version

* Mon Jun  6 2005 Marco Pesenti Gritti <mpg@redhat.com> - 0.3.1-2
- Add poppler version dep and refactor the gtk2 one

* Sun May 22 2005 Marco Pesenti Gritti <mpg@redhat.com> - 0.3.1-1
- Update to 0.3.1

* Sat May  7 2005 Marco Pesenti Gritti <mpg@redhat.com> - 0.3.0-1
- Update to 0.3.0

* Sat Apr 23 2005 Marco Pesenti Gritti <mpg@redhat.com> - 0.2.1-1
- Update to 0.2.1
- Add help support

* Wed Apr  6 2005 Marco Pesenti Gritti <mpg@redhat.com> - 0.2.0-1
- Update to 0.2.0

* Sat Mar 12 2005 Marco Pesenti Gritti <mpg@redhat.com> - 0.1.9-1
- Update to 0.1.9

* Sat Mar 12 2005 Marco Pesenti Gritti <mpg@redhat.com> - 0.1.8-1
- Update to 0.1.8

* Sat Mar  8 2005 Marco Pesenti Gritti <mpg@redhat.com> - 0.1.7-1
- Update to 0.1.7
- Install the new schemas

* Sat Mar  8 2005 Marco Pesenti Gritti <mpg@redhat.com> - 0.1.6-1
- Update to 0.1.6
- Add poppler dependency

* Sat Mar  3 2005 Marco Pesenti Gritti <mpg@redhat.com> - 0.1.5-2
- Rebuild

* Sat Feb 26 2005 Marco Pesenti Gritti <mpg@redhat.com> - 0.1.5-1
- Update to 0.1.5

* Tue Feb  9 2005 Marco Pesenti Gritti <mpg@redhat.com> - 0.1.4-1
- Update to 0.1.4
- Install schemas and update desktop database

* Tue Feb  4 2005 Marco Pesenti Gritti <mpg@redhat.com> - 0.1.3-1
- Update to 0.1.3

* Tue Feb  1 2005 Marco Pesenti Gritti <mpg@redhat.com> - 0.1.2-1
- Update to 0.1.2

* Wed Jan 26 2005 Jeremy Katz <katzj@redhat.com> - 0.1.1-1
- 0.1.1

* Thu Jan 20 2005 Jeremy Katz <katzj@redhat.com> - 0.1.0-0.20050120
- update to current cvs

* Thu Jan  6 2005 Jeremy Katz <katzj@redhat.com> - 0.1.0-0.20050106.1
- require gtk2 >= 2.6

* Thu Jan  6 2005 Jeremy Katz <katzj@redhat.com>
- Initial build.
- Add a desktop file
