# opensuse-packages

Personal RPM packaging monorepo for [OBS](https://build.opensuse.org),
hosted in the
[`home:caiobruno`](https://build.opensuse.org/project/show/home:caiobruno)
project (openSUSE Tumbleweed). The GitHub repo is the source of truth: a
merge to `main` triggers `push-to-obs`, which syncs the touched packages to
OBS, where they are built.

[![push-to-obs](https://github.com/c4i0b/opensuse-packages/actions/workflows/push-to-obs.yml/badge.svg)](https://github.com/c4i0b/opensuse-packages/actions/workflows/push-to-obs.yml)
[![validate](https://github.com/c4i0b/opensuse-packages/actions/workflows/validate.yml/badge.svg)](https://github.com/c4i0b/opensuse-packages/actions/workflows/validate.yml)
[![autoupdate](https://github.com/c4i0b/opensuse-packages/actions/workflows/autoupdate.yml/badge.svg)](https://github.com/c4i0b/opensuse-packages/actions/workflows/autoupdate.yml)
[![badges](https://github.com/c4i0b/opensuse-packages/actions/workflows/badges.yml/badge.svg)](https://github.com/c4i0b/opensuse-packages/actions/workflows/badges.yml)

## Build status

<!-- repo-badges begin -->
[![packages](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fpackages.json%3Fv%3Dfa417ed9r2)](https://build.opensuse.org/project/monitor?project=home%3Acaiobruno)
[![tumbleweed](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ftumbleweed.json%3Fv%3D89f13aa8r2)](https://build.opensuse.org/project/monitor?project=home%3Acaiobruno)
[![slowroll](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fslowroll.json%3Fv%3D224677ccr2)](https://build.opensuse.org/project/monitor?project=home%3Acaiobruno)
<!-- repo-badges end -->

<!-- build-status begin -->
*Updated 2026-11-13 21:04 UTC*
<!-- build-status end -->

## Per-package build

<!-- package-badges begin -->
[![angryoxide](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fangryoxide.json%3Fv%3Dc7efba7br2)](https://github.com/Ragnt/AngryOxide)
[![atac](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fatac.json%3Fv%3Dbf8f5515r2)](https://github.com/julien-cpsn/ATAC)
[![bandwhich](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fbandwhich.json%3Fv%3Deb1b2314r2)](https://github.com/imsnif/bandwhich)
[![bombardier](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fbombardier.json%3Fv%3D08a871d8r2)](https://github.com/codesenberg/bombardier/)
[![bully](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fbully.json%3Fv%3D3db1112br2)](https://github.com/aanarchyy/bully/)
[![cadcraft](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fcadcraft.json%3Fv%3D38c3d6b8r2)](https://github.com/storytold/cadcraft)
[![cloudflare-speed-cli](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fcloudflare-speed-cli.json%3Fv%3D1d1a9afar2)](https://github.com/kavehtehrani/cloudflare-speed-cli)
[![colloid-icon-theme](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fcolloid-icon-theme.json%3Fv%3D54179a7dr2)](https://github.com/vinceliuice/Colloid-icon-theme/)
[![crunch](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fcrunch.json%3Fv%3D959dd09er2)](https://github.com/crunchsec/crunch/)
[![crush](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fcrush.json%3Fv%3D02e44fa9r2)](https://github.com/charmbracelet/crush)
[![ctop](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fctop.json%3Fv%3Df3ac9dd7r2)](https://github.com/bcicen/ctop/)
[![deckcraft](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fdeckcraft.json%3Fv%3Debcf43c2r2)](https://github.com/storytold/deckcraft)
[![designcraft](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fdesigncraft.json%3Fv%3Dc80dc4bar2)](https://github.com/storytold/designcraft)
[![desktop-plus](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fdesktop-plus.json%3Fv%3Dbace2aaer2)](https://github.com/desktop-plus/desktop-plus/)
[![devcontainers-cli](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fdevcontainers-cli.json%3Fv%3D3bd8e76ar2)](https://github.com/devcontainers/cli)
[![dnscontrol](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fdnscontrol.json%3Fv%3Dbb2c2268r2)](https://github.com/DNSControl/dnscontrol)
[![dnspyre](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fdnspyre.json%3Fv%3D559c9123r2)](https://github.com/Tantalor93/dnspyre/)
[![dockle](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fdockle.json%3Fv%3De6a14397r2)](https://github.com/goodwithtech/dockle/)
[![effectcraft](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Feffectcraft.json%3Fv%3D876183ber2)](https://github.com/storytold/effectcraft)
[![fetch](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffetch.json%3Fv%3Da52b7bc2r2)](https://github.com/areofyl/fetch/)
[![figcraft](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffigcraft.json%3Fv%3D1fbb9f1ar2)](https://github.com/storytold/figcraft)
[![filmcraft](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffilmcraft.json%3Fv%3Dd215d201r2)](https://github.com/storytold/filmcraft)
[![fira-code-nerd-fonts](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffira-code-nerd-fonts.json%3Fv%3D00bad445r2)](https://github.com/ryanoasis/nerd-fonts/tree/master/patched-fonts/FiraCode)
[![fish-abbreviation-tips](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffish-abbreviation-tips.json%3Fv%3D9091540br2)](https://github.com/gazorby/fish-abbreviation-tips)
[![fish-autopair](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffish-autopair.json%3Fv%3D4e4a32e4r2)](https://github.com/jorgebucaran/autopair.fish)
[![fish-done](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffish-done.json%3Fv%3Dd4b2373br2)](https://github.com/franciscolourenco/done)
[![fish-fifc](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffish-fifc.json%3Fv%3D0d1f73bcr2)](https://github.com/gazorby/fifc)
[![fish-fzf](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffish-fzf.json%3Fv%3D913a5619r2)](https://github.com/patrickf1/fzf.fish)
[![fish-gitnow](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffish-gitnow.json%3Fv%3D0e494639r2)](https://github.com/joseluisq/gitnow)
[![fish-hydro](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffish-hydro.json%3Fv%3D65e8a4c2r2)](https://github.com/jorgebucaran/hydro)
[![fish-nvm](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffish-nvm.json%3Fv%3Daf83b5far2)](https://github.com/jorgebucaran/nvm.fish)
[![fish-puffer-fish](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffish-puffer-fish.json%3Fv%3D64fe7ad7r2)](https://github.com/nickeb96/puffer-fish)
[![fish-pure](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffish-pure.json%3Fv%3D28fe26bdr2)](https://github.com/pure-fish/pure)
[![fish-replay](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffish-replay.json%3Fv%3D16f6ac97r2)](https://github.com/jorgebucaran/replay.fish)
[![fish-sponge](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffish-sponge.json%3Fv%3Dc280130br2)](https://github.com/meaningful-ooo/sponge)
[![fish-tide](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffish-tide.json%3Fv%3D1abd709cr2)](https://github.com/IlanCosman/tide)
[![fish-z](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffish-z.json%3Fv%3Dbe1e60ddr2)](https://github.com/jethrokuan/z)
[![fisher](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffisher.json%3Fv%3Df591a511r2)](https://github.com/jorgebucaran/fisher/)
[![fluent-icon-theme](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffluent-icon-theme.json%3Fv%3Dcc8165abr2)](https://github.com/vinceliuice/Fluent-icon-theme/)
[![gridcraft](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fgridcraft.json%3Fv%3D04498ef6r2)](https://github.com/storytold/gridcraft)
[![httpx](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fhttpx.json%3Fv%3D8b2b022fr2)](https://github.com/projectdiscovery/httpx/)
[![hydra-launcher](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fhydra-launcher.json%3Fv%3D608e73eer2)](https://github.com/hydralauncher/hydra/)
[![jetbrains-mono-nerd-fonts](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fjetbrains-mono-nerd-fonts.json%3Fv%3D05b5a695r2)](https://github.com/ryanoasis/nerd-fonts/tree/master/patched-fonts/JetBrainsMono)
[![lazydocker](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Flazydocker.json%3Fv%3D090ec765r2)](https://github.com/jesseduffield/lazydocker/)
[![lightcraft](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Flightcraft.json%3Fv%3D177297d5r2)](https://github.com/storytold/lightcraft)
[![ludusavi](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fludusavi.json%3Fv%3Db87a33cdr2)](https://github.com/mtkennerly/ludusavi)
[![mangojuice](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fmangojuice.json%3Fv%3D254cc118r2)](https://github.com/radiolamp/mangojuice/)
[![masscan](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fmasscan.json%3Fv%3Da55f16a6r2)](https://github.com/robertdavidgraham/masscan/)
[![mdk4](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fmdk4.json%3Fv%3Dee67f7ber2)](https://github.com/aircrack-ng/mdk4/)
[![meslo-nerd-fonts](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fmeslo-nerd-fonts.json%3Fv%3Dcdbaa176r2)](https://github.com/ryanoasis/nerd-fonts/tree/master/patched-fonts/Meslo)
[![mise](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fmise.json%3Fv%3D2f4c8d77r2)](https://github.com/jdx/mise)
[![naabu](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fnaabu.json%3Fv%3D91044643r2)](https://github.com/projectdiscovery/naabu/)
[![netscanner](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fnetscanner.json%3Fv%3D1952cb9fr2)](https://github.com/Chleba/netscanner)
[![nexttrace](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fnexttrace.json%3Fv%3Dd8598c93r2)](https://github.com/nxtrace/NTrace-core/)
[![nuclei](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fnuclei.json%3Fv%3D023a0d75r2)](https://github.com/projectdiscovery/nuclei/)
[![oha](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Foha.json%3Fv%3D1fe036c0r2)](https://github.com/hatoo/oha)
[![omo](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fomo.json%3Fv%3D1755b27br2)](https://github.com/code-yeongyu/oh-my-openagent/)
[![opencode-desktop](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fopencode-desktop.json%3Fv%3D4762f56cr2)](https://github.com/anomalyco/opencode/)
[![oxker](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Foxker.json%3Fv%3Dd5f5a968r2)](https://github.com/mrjackwills/oxker)
[![pdfcraft](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fpdfcraft.json%3Fv%3D6f90cf0cr2)](https://github.com/storytold/pdfcraft)
[![pear-desktop](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fpear-desktop.json%3Fv%3Dba61723cr2)](https://github.com/pear-devs/pear-desktop/)
[![photocraft](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fphotocraft.json%3Fv%3D928be736r2)](https://github.com/storytold/photocraft)
[![press-start-2p-fonts](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fpress-start-2p-fonts.json%3Fv%3Dae343c68r2)](https://fonts.google.com/specimen/Press+Start+2P)
[![python3-libusb-package](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fpython3-libusb-package.json%3Fv%3D5e2f63b5r2)](https://github.com/pyocd/libusb-package)
[![qogir-icon-theme](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fqogir-icon-theme.json%3Fv%3Dd01bfab2r2)](https://github.com/vinceliuice/Qogir-icon-theme/)
[![rathole](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Frathole.json%3Fv%3D3895012dr2)](https://github.com/rathole-org/rathole)
[![rio](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Frio.json%3Fv%3D8f698540r2)](https://github.com/raphamorim/rio/)
[![scientifica-fonts](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fscientifica-fonts.json%3Fv%3De3e5b782r2)](https://github.com/oppiliappan/scientifica)
[![selawik-fonts](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fselawik-fonts.json%3Fv%3D4479f401r2)](https://github.com/microsoft/Selawik)
[![slimbrave](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fslimbrave.json%3Fv%3Df88aed07r2)](https://github.com/ChaoticSi1ence/SlimBrave-Neo/)
[![solidcraft](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fsolidcraft.json%3Fv%3Daf544fc0r2)](https://github.com/tangency-labs/solidcraft)
[![soundcraft](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fsoundcraft.json%3Fv%3Db60a9018r2)](https://github.com/storytold/soundcraft)
[![superfile](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fsuperfile.json%3Fv%3D637b83dcr2)](https://github.com/yorukot/superfile/)
[![tela-icon-theme](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ftela-icon-theme.json%3Fv%3D15740ae4r2)](https://github.com/vinceliuice/Tela-icon-theme/)
[![television](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ftelevision.json%3Fv%3D7788fe9br2)](https://github.com/alexpasmantier/television)
[![topmatic](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ftopmatic.json%3Fv%3Db88abaf9r2)](https://github.com/c4i0b/topmatic/)
[![unimatrix](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Funimatrix.json%3Fv%3D66b42c4ar2)](https://github.com/will8211/unimatrix)
[![vectorcraft](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fvectorcraft.json%3Fv%3D4c085731r2)](https://github.com/storytold/vectorcraft)
[![ventoy](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fventoy.json%3Fv%3D074f0e3er2)](https://github.com/ventoy/Ventoy/)
[![waydroid-helper](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fwaydroid-helper.json%3Fv%3D18da9989r2)](https://github.com/waydroid-helper/waydroid-helper/)
[![whitesur-icon-theme](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fwhitesur-icon-theme.json%3Fv%3D1c0168c4r2)](https://github.com/vinceliuice/WhiteSur-icon-theme/)
[![whosthere](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fwhosthere.json%3Fv%3D0a26b9b4r2)](https://github.com/ramonvermeulen/whosthere)
[![wifit3](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fwifit3.json%3Fv%3Dac11aaadr2)](https://github.com/derv82/wifit3/)
[![wifite](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fwifite.json%3Fv%3Dc1bbcecar2)](https://github.com/derv82/wifite2/)
[![wordcraft](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fwordcraft.json%3Fv%3Dbee98fdfr2)](https://github.com/storytold/wordcraft)
[![ytm-player](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fytm-player.json%3Fv%3D5cb2171br2)](https://github.com/peternaame-boop/ytm-player/)
[![zapzap](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fzapzap.json%3Fv%3Dca15279fr2)](https://github.com/rafatosta/zapzap)
<!-- package-badges end -->

## Install (openSUSE Tumbleweed)

    zypper ar -f https://download.opensuse.org/repositories/home:/caiobruno/opensuse_tumbleweed/home:caiobruno.repo
    zypper ref
    zypper in <package>

## How it works

### Automatic updates

```
upstream release
       │
       ▼  every 4h, per packages/<name>/upstream
┌───────────┐   bump spec + _service
│ autoupdate│──────────────▶ main, after the in-job
└───────────┘               gate (version + asset
                             HEAD checks, validate)
                                 │  GITHUB_TOKEN fires no push event:
                                 ▼  push-to-obs rides workflow_run
                     push-to-obs syncs the touched
                     packages to OBS → OBS builds
                                 │
                                 ▼  ~1h20 after the bump
                     badges refresh (README + badges/*.json)
```

- Each package lives in `packages/<name>/`. Required: `*.spec`. Optional:
  `_service`, `fetch.sh`, `bump.sh`, `BIN`, `.obsignore`, `<name>.rpmlintrc`,
  `<name>.changes`.
- `tools/project-meta.sh` renders the OBS project meta (repos, arches):
  Tumbleweed (x86_64) and Slowroll (x86_64).
- Each package's `_service` tells OBS to fetch official upstream release
  artifacts server-side, so no archives are committed.
- A scheduled workflow (`autoupdate`) checks upstream releases (per
  package's `upstream` file) and bumps the spec and `_service`
  automatically; Dependabot keeps Actions updated.

See [docs/](docs/README.md) for the full picture.

## Development

The host needs only `just` + `podman`; everything else runs in the
ephemeral tooling container ([docs/environment.md](docs/environment.md)).

    just image                      # once: build the tooling container + wire hooks
    just lint                       # lint the repo (run before push)
    just build packages/<name>      # pre-flight local rpmbuild, rpmlint-gated
    just push packages/<name> "msg" # lint, then sync to OBS and commit

## Adding a package

1. `just new-pkg <name>` scaffolds from [templates/](templates/)
   (`templates/*.spec.tpl`); fill the OBS title/description from the
   spec.
2. Add a `_service` so OBS fetches upstream sources, plus `bump.sh`/
   `fetch.sh` for version updates.
3. Add `packages/<name>/upstream` (`owner/repo`, `tags:owner/repo` or
   `npm:<package>`) so autoupdate tracks it.
4. `just push packages/<name> "initial package"`: the package only exists
   on OBS after push.
5. Manual bump, if ever needed: `just bump packages/<name> <version>`.
