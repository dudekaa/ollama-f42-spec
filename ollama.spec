# Platforms that aren't supported by official builds
ExcludeArch:    ppc64le s390x

%define packagePatch 1
%global debug_package %{nil}

Name:    ollama
Epoch:   1
Version: 0.11.9
Release: %{packagePatch}%{?dist}
Summary: Get up and running AI LLMs

License: Apache-2.0 AND MIT
URL:     https://github.com/ollama/ollama
%ifarch x86_64
Source: https://github.com/ollama/ollama/releases/download/v%{version}/ollama-linux-amd64.tgz
Source1: https://github.com/ollama/ollama/releases/download/v%{version}/ollama-linux-amd64-rocm.tgz
%endif
%ifarch aarch64
Source: https://github.com/ollama/ollama/releases/download/v%{version}/ollama-linux-arm64.tgz
#% else
#% {error:Unsupported architecture %{_arch}}
%endif

BuildRequires:  systemd-rpm-macros
BuildRequires:  tar
BuildRequires:  chrpath
Requires(pre):  shadow-utils
Requires(pre):  /usr/bin/getent
Requires:       systemd
%ifarch x86_64
Requires:       hipblas
Requires:       rocblas
%endif

%description %{expand:
Get up and running with Llama 3.2, Mistral, Gemma 2, and other large language
models.
}

%pre
# Create ollama group if it doesn't exist
getent group ollama >/dev/null || groupadd -r ollama

# Create ollama user if it doesn't exist
getent passwd ollama >/dev/null || \
    useradd -r -g ollama -d %{_localstatedir}/lib/ollama \
            -s /sbin/nologin -c "Ollama AI Service" ollama

# Create home directory if it doesn't exist
if [ ! -d %{_localstatedir}/lib/ollama ]; then
    mkdir -p %{_localstatedir}/lib/ollama
    chown ollama:ollama %{_localstatedir}/lib/ollama
    chmod 755 %{_localstatedir}/lib/ollama
fi


%prep
%setup -c
%ifarch x86_64
%setup -c -T -D -a 1
%endif


%install
# Install ollama files
mkdir -p %{buildroot}/usr/
cp -ar %{_builddir}/%{name}-%{version}/* %{buildroot}/usr/

# remove copies of system libraries
runtime_removal="hipblas rocblas amdhip64 rocsolver amd_comgr hsa-runtime64 rocsparse tinfo rocprofiler-register drm drm_amdgpu numa elf"
for rr in $runtime_removal; do
    rm -rf %{buildroot}/usr/lib/ollama/rocm/lib${rr}*
done
rm -rf %{buildroot}/usr/lib/ollama/rocm/rocblas

rmdir %{buildroot}/usr/lib/ollama/rocm

# Remove problematic RPATH entries from libggml-hip.so
chrpath --delete %{buildroot}/usr/lib/ollama/libggml-hip.so 2>/dev/null

# Install systemd service file
mkdir -p %{buildroot}%{_unitdir}
cat << EOF > %{buildroot}%{_unitdir}/%{name}.service
[Unit]
Description=Ollama Service
After=network-online.target

[Service]
ExecStart=/usr/bin/ollama serve
User=ollama
Group=ollama
Restart=always
RestartSec=3
Environment="PATH=$PATH"

[Install]
WantedBy=multi-user.target
EOF


%files
%defattr(-,root,root)
%attr(0755,-,-)%{_bindir}/%{name}
%dir %ghost %attr(0755,ollama,ollama) %{_localstatedir}/lib/ollama
%{_prefix}/lib/%{name}
%attr(0644,-,-)%{_unitdir}/%{name}.service


%post
%systemd_post %{name}.service

%preun
# Stop the service first
%systemd_preun %{name}.service

# Clean up on complete removal (not upgrade)
if [ $1 -eq 0 ]; then
    # Remove copied files, the % dir macro will handle the rest
    rm -rf /usr/lib/%{name}

    # Remove downloaded models and cache
    rm -rf %{_localstatedir}/lib/ollama/models
    rm -rf %{_localstatedir}/cache/ollama
fi

%postun
%systemd_postun_with_restart %{name}.service

# Only remove user on complete uninstall (not upgrade)
if [ $1 -eq 0 ]; then
    # Stop and disable service first (should already be done by systemd macros)
    systemctl stop %{name}.service 2>/dev/null || true
    systemctl disable %{name}.service 2>/dev/null || true

    # Remove user and group (optional - some admins prefer to keep them)
    # userdel ollama 2>/dev/null || true
    # groupdel ollama 2>/dev/null || true

    # Optionally remove user data (be very careful here!)
    # rm -rf %{_localstatedir}/lib/ollama
fi

%changelog
* Thu Sep 04 2025 Arnošt Dudek <arnost@arnostdudek.cz> - 0.11.9-1
- Initial build
