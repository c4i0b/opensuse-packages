Name:           fish-fifc
Version:        0.3.4
Release:        0
Summary:        Fzf powered fish history and tab completions
License:        MIT
URL:            https://github.com/gazorby/fifc
Source0:        fish-fifc-%{version}.tar.gz
BuildArch:      noarch

Requires:       fish
Requires:       fzf
Requires:       file
# optional upstream, required here for the full preview experience
Requires:       bat
Requires:       eza
Requires:       fd
Requires:       chafa
Requires:       hexyl
Requires:       ripgrep
# broot upgrades ctrl-o on a directory to an interactive tree; without it
# the shortcut falls back to eza above
Recommends:     broot

%description
Fzf powered fish history and tab completions, with smart file previews
picked per file type: bat for text, eza for directories, chafa for images
and hexyl for binaries.

%prep
%setup -q -n fifc-%{version}
# broot's first-run "install the br function?" dialog must not fire from
# inside the fzf ctrl-o: skip it with broot's own env knob
sed -i 's/broot --color=yes/env BR_INSTALL=no broot --color=yes/' \
    functions/_fifc_open_dir.fish
# late \t rebinders (autopair's --on-variable handler) clobber our TAB
# binding (fifc issue #81): re-apply on the same event, registered after
cat >> conf.d/fifc.fish <<'FIFOEOF'

function __fifc_rebind_tab --on-variable fish_key_bindings
    if status is-interactive
        for mode in default insert
            bind --mode $mode $fifc_keybinding _fifc
        end
    end
end
FIFOEOF

%build

%install
install_vendor() {
  # $2: vendor subdir; conf.d already ends in .d, the others do not
  [ -d "$1" ] || return 0
  for f in "$1"/*.fish; do
    install -Dpm644 "$f" "%{buildroot}%{_datadir}/fish/vendor_$2/$(basename "$f")"
  done
}
install_vendor conf.d conf.d
install_vendor functions functions.d
install_vendor completions completions.d

%files
%license LICENSE
%dir %{_datadir}/fish
%dir %{_datadir}/fish/vendor_conf.d
%{_datadir}/fish/vendor_conf.d/*.fish
%dir %{_datadir}/fish/vendor_functions.d
%{_datadir}/fish/vendor_functions.d/*.fish
%dir %{_datadir}/fish/vendor_completions.d
%{_datadir}/fish/vendor_completions.d/*.fish

%changelog
