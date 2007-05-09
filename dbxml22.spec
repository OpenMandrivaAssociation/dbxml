%define db_version 43
%define dbxml_version 2.2.13
%define libdbxml %mklibname dbxml 2.2

%define with_java 0
%{?_with_java: %{expand: %%global with_java 1}}

Name: dbxml
Version: %{dbxml_version}
Release: %mkrel 12
Group: Development/Libraries
Summary: Berkeley DB XML
URL: http://www.sleepycat.com/products/xml.shtml
License:  Other License(s), see package, BSD
Source0: dbxml-%{dbxml_version}.tar.gz
Patch0: dbxml-2.2.13-rpath.patch
Patch1: patch.2.2.13.1
Patch2: patch.2.2.13.2
Patch3: patch.2.2.13.3
Patch4: patch.2.2.13.4
Patch5: patch.2.2.13.5
Patch6: patch.2.2.13.6
Patch7: dbxml-2.2.13-dbxml-install.patch
BuildRequires: db4.3-devel
BuildRequires: xerces-c-devel 
BuildRequires: libicu-devel 
BuildRequires: update-alternatives
%if %with_java
BuildRequires: jpackage-utils
BuildRequires: java-devel >= 1.5.0
%endif
BuildRoot: %{_tmppath}/%{name}-%{version}-build

%description
This is the Berkeley DB XML from Sleepycat Software.

#------------------------------------------------------------------------

%package -n %libdbxml
Summary: Berkeley DB XML
Group: Development/Libraries

%description -n %libdbxml
Berkeley DB XML

%files -n %libdbxml
%defattr(-,root,root)
%{_libdir}/libdbxml-2.2.so
%{_libdir}/libxquery-1.2.so
%{_libdir}/libxquery-1.so
%{_libdir}/libpathan.so.*

#------------------------------------------------------------------------

%if %with_java

%package -n dbxml-java
Summary: Berkeley DB XML Java
Group: Development/Libraries

%description -n dbxml-java
Berkeley DB XML Java

%files -n dbxml-java
%defattr(-,root,root)
%{_javadir}/dbxml.jar
%{_libdir}/libdbxml_java-2.2.so
%{_libdir}/libdbxml_java-2.2_g.so

%endif

#------------------------------------------------------------------------

%package utils
Summary: Berkeley DB XML
Group: Development/Libraries
Requires: %libdbxml = %{version}

%description utils
This is the Berkeley DB XML from Sleepycat Software.

%files utils
%defattr(0755,root,root)
%_bindir/*

#------------------------------------------------------------------------

%package -n %libdbxml-devel
Summary: Berkeley DB XML development libraries
Group: Development/Libraries
Requires: xerces-c-devel
Requires: db4.3-devel
Requires: libstdc++-devel 
Requires: %libdbxml = %version
%if %with_java
Requires: dbxml-java = %version
%endif
Provides: dbxml-devel = %version
Provides: libdbxml-devel = %version

%description -n %libdbxml-devel
These are development libraries and headers for the Berkeley DB XML
from Sleepycat Software.

%files -n %libdbxml-devel 
%defattr(-,root,root)
%{_includedir}/*
%{_libdir}/libdbxml-2.so       
%{_libdir}/libdbxml-2.2.la 
%{_libdir}/libdbxml.so         
%{_libdir}/libxquery.so
%{_libdir}/libxquery-1.2.la
%{_libdir}/libpathan.so
%{_libdir}/libpathan.la
%if %with_java
%{_libdir}/libdbxml_java-2.so  
%{_libdir}/libdbxml_java.so
%{_libdir}/libdbxml_java-2.2.la
%endif

#------------------------------------------------------------------------

%package -n %libdbxml-static-devel
Summary: Berkeley DB XML development libraries
Group: Development/Libraries
Requires: %libdbxml-devel = %{version}

%description -n %libdbxml-static-devel
These are development libraries and headers for the Berkeley DB XML
from Sleepycat Software.

%files -n %libdbxml-static-devel
%defattr(-,root,root)
%{_libdir}/*.a

#------------------------------------------------------------------------

%package doc
Summary: Berkeley DB XML development libraries
Group: Development/Libraries

%description doc
These are development libraries and headers for the Berkeley DB XML
from Sleepycat Software.

%files doc
%defattr(-,root,root)
%doc %{_defaultdocdir}/dbxml

#------------------------------------------------------------------------

%prep
%setup -q
find . -type d | xargs chmod 755
find . -type f | xargs chmod +w
%patch0 -p1 -b .rpath
pushd dbxml
%patch1 -p0
popd
%patch2 -p1
%patch3 -p1
%patch4 -p1 
%patch5 -p1 
%patch6 -p1 
%patch7 -p1 

%build
%if %with_java
    source %_sysconfdir/java/java.conf
%endif

CFLAGS="%{optflags} -fPIC "
CXXFLAGS="%{optflags} -fPIC"
CPPFLAGS="-I%_includedir/db4" 
export CFLAGS CXXFLAGS CPPFLAGS

#################  build pathan static only

pushd pathan
    libtoolize --copy --force && aclocal && autoconf
    export PATHAN_BUILDROOT=${PWD}
    %if "%_lib" != "lib"
        sed -i "s,/lib/,/lib64/,g" configure
    %endif
    %configure2_5x \
    %if "%_lib" != "lib"
        --with-lib64 \
    %endif
        --with-xerces=%_prefix

    %if "%_lib" != "lib"
        ln -sf lib lib64
    %endif
    make
popd

#################  build xquery static only

pushd xquery-1.2.0
    export XQUERY_BUILDROOT=${PWD}
    cd dist
    ./s_config
    ./s_all
    %if "%_lib" != "lib"
        sed -i "s,/lib/,/lib64/,g" configure
    %endif

    CONFIGURE_TOP=${PWD}

    cd ../build_unix

    %configure2_5x \
    %if "%_lib" != "lib"
        --with-lib64 \
    %endif
        --with-xerces=%_prefix \
        --with-pathan=${PATHAN_BUILDROOT} 

    %if "%_lib" != "lib"
        ln -sf lib lib64
    %endif

    make
popd

#################  build dbxml

pushd dbxml/dist
%if %with_java
    export ADDITIONAL_CLASSPATH=":%_datadir/java/db.jar"
%endif
    ./s_config
    ./s_all
    %if "%_lib" != "lib"
        sed -i "s,/lib/,/lib64/,g" configure
    %endif
    
    CONFIGURE_TOP=${PWD}

    cd ../build_unix

    %configure2_5x \
%if %with_java
    --enable-java \
%else
    --disable-java \
%endif
    --with-pathan=${PATHAN_BUILDROOT} \
    --with-xquery=${XQUERY_BUILDROOT} \
    --with-xerces=%_prefix \
    --with-berkeleydb=%_prefix 

    make
popd

%install
rm -rf %buildroot
for name in pathan xquery-1.2.0/build_unix dbxml/build_unix; do
    pushd ${name}
        make DESTDIR=%buildroot install
    popd
done

%if %with_java
# Move jar to proper place
mkdir -p %buildroot%_datadir/java
mv %buildroot%_libdir/dbxml.jar %buildroot%_datadir/java/dbxml.jar
%endif

# install docs
mkdir -p %buildroot%_defaultdocdir/dbxml
cp -a dbxml/docs/* %buildroot%_defaultdocdir/dbxml

%clean
rm -rf $RPM_BUILD_ROOT

