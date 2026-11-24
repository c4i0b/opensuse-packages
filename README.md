# opensuse-packages

Personal RPM packaging monorepo for [OBS](https://build.opensuse.org),
hosted in the
[`home:caiobruno`](https://build.opensuse.org/project/show/home:caiobruno)
project (openSUSE Tumbleweed and Slowroll). The GitHub repo is the source of
truth: a merge to `main` triggers `push-to-obs`, which syncs the touched
packages to OBS, where they are built.

[![push-to-obs](https://github.com/c4i0b/opensuse-packages/actions/workflows/push-to-obs.yml/badge.svg)](https://github.com/c4i0b/opensuse-packages/actions/workflows/push-to-obs.yml)
[![validate](https://github.com/c4i0b/opensuse-packages/actions/workflows/validate.yml/badge.svg)](https://github.com/c4i0b/opensuse-packages/actions/workflows/validate.yml)
[![autoupdate](https://github.com/c4i0b/opensuse-packages/actions/workflows/autoupdate.yml/badge.svg)](https://github.com/c4i0b/opensuse-packages/actions/workflows/autoupdate.yml)
[![badges](https://github.com/c4i0b/opensuse-packages/actions/workflows/badges.yml/badge.svg)](https://github.com/c4i0b/opensuse-packages/actions/workflows/badges.yml)

## Build status

<!-- repo-badges begin -->
[![packages](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fpackages.json%3Fv%3Dcb7456bar2)](https://build.opensuse.org/project/monitor?project=home%3Acaiobruno)
[![tumbleweed](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ftumbleweed.json%3Fv%3Dd7a0f713r2)](https://build.opensuse.org/project/monitor?project=home%3Acaiobruno)
[![slowroll](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fslowroll.json%3Fv%3Da5b98dd9r2)](https://build.opensuse.org/project/monitor?project=home%3Acaiobruno)
<!-- repo-badges end -->

<!-- build-status begin -->

*Updated 2026-11-24 21:30 UTC*
<!-- build-status end -->

## Per-package build

<!-- package-badges begin -->
[![angryoxide](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fangryoxide.json%3Fv%3D59348e65r2)](https://github.com/Ragnt/AngryOxide/)
[![atac](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fatac.json%3Fv%3D78d316ffr2)](https://github.com/julien-cpsn/ATAC/)
[![bandwhich](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fbandwhich.json%3Fv%3D2ced91f4r2)](https://github.com/imsnif/bandwhich/)
[![bombardier](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fbombardier.json%3Fv%3D7cc0a996r2)](https://github.com/codesenberg/bombardier/)
[![bully](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fbully.json%3Fv%3D9df1969er2)](https://github.com/aanarchyy/bully/)
[![cadcraft](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fcadcraft.json%3Fv%3D04c17811r2)](https://github.com/storytold/cadcraft/)
[![cloudflare-speed-cli](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fcloudflare-speed-cli.json%3Fv%3Df3d295f4r2)](https://github.com/kavehtehrani/cloudflare-speed-cli/)
[![colloid-icon-theme](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fcolloid-icon-theme.json%3Fv%3D90b6a660r2)](https://github.com/vinceliuice/Colloid-icon-theme/)
[![crunch](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fcrunch.json%3Fv%3Db4727de5r2)](https://github.com/crunchsec/crunch)
[![crush](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fcrush.json%3Fv%3D733b45ear2)](https://github.com/charmbracelet/crush/)
[![ctop](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fctop.json%3Fv%3De94e180cr2)](https://github.com/bcicen/ctop/)
[![deckcraft](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fdeckcraft.json%3Fv%3D85103aefr2)](https://github.com/storytold/deckcraft/)
[![designcraft](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fdesigncraft.json%3Fv%3D483f60d1r2)](https://github.com/storytold/designcraft/)
[![desktop-plus](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fdesktop-plus.json%3Fv%3D789a47dar2)](https://github.com/desktop-plus/desktop-plus/)
[![devcontainers-cli](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fdevcontainers-cli.json%3Fv%3D565bbb1fr2)](https://github.com/devcontainers/cli)
[![dnscontrol](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fdnscontrol.json%3Fv%3D14975303r2)](https://github.com/DNSControl/dnscontrol/)
[![dnspyre](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fdnspyre.json%3Fv%3D472210ccr2)](https://github.com/Tantalor93/dnspyre/)
[![dockle](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fdockle.json%3Fv%3D97869396r2)](https://github.com/goodwithtech/dockle/)
[![effectcraft](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Feffectcraft.json%3Fv%3D7af0c1fbr2)](https://github.com/storytold/effectcraft/)
[![fetch](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffetch.json%3Fv%3D3929bd83r2)](https://github.com/areofyl/fetch/)
[![figcraft](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffigcraft.json%3Fv%3Db6a9db07r2)](https://github.com/storytold/figcraft/)
[![filmcraft](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffilmcraft.json%3Fv%3D9afd2be4r2)](https://github.com/storytold/filmcraft/)
[![fira-code-nerd-fonts](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffira-code-nerd-fonts.json%3Fv%3Dce1acee9r2)](https://github.com/ryanoasis/nerd-fonts/)
[![fish-abbreviation-tips](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffish-abbreviation-tips.json%3Fv%3D5f478097r2)](https://github.com/gazorby/fish-abbreviation-tips/)
[![fish-autopair](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffish-autopair.json%3Fv%3D6b3c4867r2)](https://github.com/jorgebucaran/autopair.fish/)
[![fish-done](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffish-done.json%3Fv%3D33f2a820r2)](https://github.com/franciscolourenco/done/)
[![fish-fifc](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffish-fifc.json%3Fv%3Deccbc9bbr2)](https://github.com/gazorby/fifc/)
[![fish-fzf](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffish-fzf.json%3Fv%3D379d62e9r2)](https://github.com/patrickf1/fzf.fish/)
[![fish-gitnow](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffish-gitnow.json%3Fv%3D807c60fbr2)](https://github.com/joseluisq/gitnow/)
[![fish-hydro](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffish-hydro.json%3Fv%3Da718d2aer2)](https://github.com/jorgebucaran/hydro/)
[![fish-nvm](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffish-nvm.json%3Fv%3D0a705f25r2)](https://github.com/jorgebucaran/nvm.fish/)
[![fish-puffer-fish](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffish-puffer-fish.json%3Fv%3Da5df00f8r2)](https://github.com/nickeb96/puffer-fish/)
[![fish-pure](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffish-pure.json%3Fv%3D034fcb23r2)](https://github.com/pure-fish/pure/)
[![fish-replay](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffish-replay.json%3Fv%3D3168e0b3r2)](https://github.com/jorgebucaran/replay.fish/)
[![fish-sponge](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffish-sponge.json%3Fv%3D69405861r2)](https://github.com/meaningful-ooo/sponge/)
[![fish-tide](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffish-tide.json%3Fv%3D369b9318r2)](https://github.com/IlanCosman/tide/)
[![fish-z](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffish-z.json%3Fv%3D535cacf0r2)](https://github.com/jethrokuan/z/)
[![fisher](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffisher.json%3Fv%3D03dccbedr2)](https://github.com/jorgebucaran/fisher/)
[![fluent-icon-theme](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffluent-icon-theme.json%3Fv%3Dd9d72f7cr2)](https://github.com/vinceliuice/Fluent-icon-theme/)
[![gridcraft](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fgridcraft.json%3Fv%3D3384bd32r2)](https://github.com/storytold/gridcraft/)
[![hermes-agent](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fhermes-agent.json%3Fv%3Df62617b9r2)](https://github.com/NousResearch/hermes-agent/)
[![httpx](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fhttpx.json%3Fv%3D677a2b1fr2)](https://github.com/projectdiscovery/httpx/)
[![hydra-launcher](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fhydra-launcher.json%3Fv%3D56bb8867r2)](https://github.com/hydralauncher/hydra/)
[![jetbrains-mono-nerd-fonts](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fjetbrains-mono-nerd-fonts.json%3Fv%3D8d6f63a2r2)](https://github.com/ryanoasis/nerd-fonts/)
[![lazydocker](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Flazydocker.json%3Fv%3Dfd17f81br2)](https://github.com/jesseduffield/lazydocker/)
[![lightcraft](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Flightcraft.json%3Fv%3D9208e0fbr2)](https://github.com/storytold/lightcraft/)
[![limusic](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Flimusic.json%3Fv%3D14a96cf6r2)](https://github.com/SimoHypers/limusic/)
[![ludusavi](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fludusavi.json%3Fv%3D7785654cr2)](https://github.com/mtkennerly/ludusavi/)
[![mangojuice](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fmangojuice.json%3Fv%3D4a823a3cr2)](https://github.com/radiolamp/mangojuice/)
[![masscan](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fmasscan.json%3Fv%3D34c2956dr2)](https://github.com/robertdavidgraham/masscan/)
[![mdk4](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fmdk4.json%3Fv%3D5aeee3f6r2)](https://github.com/aircrack-ng/mdk4/)
[![meslo-nerd-fonts](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fmeslo-nerd-fonts.json%3Fv%3Dc2212486r2)](https://github.com/ryanoasis/nerd-fonts/)
[![mise](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fmise.json%3Fv%3D85e386ear2)](https://github.com/jdx/mise/)
[![naabu](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fnaabu.json%3Fv%3D12b42637r2)](https://github.com/projectdiscovery/naabu/)
[![netscanner](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fnetscanner.json%3Fv%3D0b8c187dr2)](https://github.com/Chleba/netscanner/)
[![nexttrace](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fnexttrace.json%3Fv%3De16d4eb5r2)](https://github.com/nxtrace/NTrace-core/)
[![nuclei](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fnuclei.json%3Fv%3Dea99a975r2)](https://github.com/projectdiscovery/nuclei/)
[![oha](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Foha.json%3Fv%3D1c4e6d29r2)](https://github.com/hatoo/oha/)
[![omo](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fomo.json%3Fv%3D4b42d770r2)](https://github.com/code-yeongyu/oh-my-openagent/)
[![openclaw](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fopenclaw.json%3Fv%3D58e9dcc1r2)](https://github.com/openclaw/openclaw)
[![opencode-desktop](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fopencode-desktop.json%3Fv%3D003b7420r2)](https://github.com/anomalyco/opencode/)
[![oxker](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Foxker.json%3Fv%3Db0773d4ar2)](https://github.com/mrjackwills/oxker/)
[![pdfcraft](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fpdfcraft.json%3Fv%3D3496705ar2)](https://github.com/storytold/pdfcraft/)
[![pear-desktop](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fpear-desktop.json%3Fv%3D16d322d9r2)](https://github.com/pear-devs/pear-desktop/)
[![phonebox](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fphonebox.json%3Fv%3D8fc4ef79r2)](https://github.com/ersinkoc/phonebox/)
[![photocraft](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fphotocraft.json%3Fv%3D824a286ar2)](https://github.com/storytold/photocraft/)
[![press-start-2p-fonts](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fpress-start-2p-fonts.json%3Fv%3D6bbe3cf8r2)](https://fonts.google.com/specimen/Press+Start+2P)
[![python3-libusb-package](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fpython3-libusb-package.json%3Fv%3D7713044fr2)](https://github.com/pyocd/libusb-package/)
[![qogir-icon-theme](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fqogir-icon-theme.json%3Fv%3D85ce3064r2)](https://github.com/vinceliuice/Qogir-icon-theme/)
[![rathole](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Frathole.json%3Fv%3D305f670fr2)](https://github.com/rathole-org/rathole/)
[![rea-agents](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Frea-agents.json%3Fv%3Db126b364r2)](https://github.com/morluto/rea)
[![rio](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Frio.json%3Fv%3Da2603e61r2)](https://github.com/raphamorim/rio/)
[![scientifica-fonts](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fscientifica-fonts.json%3Fv%3D6ecbac50r2)](https://github.com/oppiliappan/scientifica/)
[![selawik-fonts](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fselawik-fonts.json%3Fv%3Dcfe2ed19r2)](https://github.com/microsoft/Selawik/)
[![slimbrave](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fslimbrave.json%3Fv%3D3161a424r2)](https://github.com/ChaoticSi1ence/SlimBrave-Neo/)
[![solidcraft](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fsolidcraft.json%3Fv%3D99e33c04r2)](https://github.com/tangency-labs/solidcraft/)
[![soundcraft](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fsoundcraft.json%3Fv%3D4f5bc942r2)](https://github.com/storytold/soundcraft/)
[![spotube](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fspotube.json%3Fv%3D474b47ffr2)](https://github.com/team-spotube/Spotube/)
[![superfile](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fsuperfile.json%3Fv%3D1faa1a69r2)](https://github.com/yorukot/superfile/)
[![tela-icon-theme](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ftela-icon-theme.json%3Fv%3D1b79df7cr2)](https://github.com/vinceliuice/Tela-icon-theme/)
[![television](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ftelevision.json%3Fv%3Df38a3f35r2)](https://github.com/alexpasmantier/television/)
[![topmatic](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ftopmatic.json%3Fv%3D00952766r2)](https://github.com/c4i0b/topmatic/)
[![unimatrix](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Funimatrix.json%3Fv%3D6d08a197r2)](https://github.com/will8211/unimatrix/)
[![vectorcraft](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fvectorcraft.json%3Fv%3Dccc8de69r2)](https://github.com/storytold/vectorcraft/)
[![ventoy](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fventoy.json%3Fv%3D4bdf29car2)](https://github.com/ventoy/Ventoy/)
[![waydroid-helper](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fwaydroid-helper.json%3Fv%3D56688f8dr2)](https://github.com/waydroid-helper/waydroid-helper/)
[![whitesur-icon-theme](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fwhitesur-icon-theme.json%3Fv%3Dc9fc890br2)](https://github.com/vinceliuice/WhiteSur-icon-theme/)
[![whosthere](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fwhosthere.json%3Fv%3Da0ad1b7br2)](https://github.com/ramonvermeulen/whosthere/)
[![wifit3](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fwifit3.json%3Fv%3D2435ff28r2)](https://github.com/derv82/wifit3/)
[![wifite](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fwifite.json%3Fv%3D155d3e83r2)](https://github.com/derv82/wifite2/)
[![wordcraft](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fwordcraft.json%3Fv%3Dbda017c2r2)](https://github.com/storytold/wordcraft/)
[![ytm-player](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fytm-player.json%3Fv%3Db14ec722r2)](https://github.com/peternaame-boop/ytm-player/)
[![zapzap](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fzapzap.json%3Fv%3Dc2c5efd2r2)](https://github.com/rafatosta/zapzap/)
<!-- package-badges end -->

## Install

    # openSUSE Tumbleweed
    zypper ar -f https://download.opensuse.org/repositories/home:/caiobruno/opensuse_tumbleweed/home:caiobruno.repo
    # openSUSE Slowroll
    zypper ar -f https://download.opensuse.org/repositories/home:/caiobruno/opensuse_slowroll/home:caiobruno.repo
    zypper ref
    zypper in <package>

## How it works

### Automatic updates

```
 (upstream release)
  |
  |  3x/day scan @ 01:23 / 09:23 / 17:23 UTC (data-driven slots,
  |  see docs/autoupdate.md)
  |
  o  AUTOUPDATE BOT .......... bump spec + _service, re-vendor in CI
  |                          (gate red -> only that package reverts)
  |
  o  IN-JOB GATE ............ version + asset HEAD + lint/drift
  |
  o  MAIN ................... ff-merge of the gated SHA
  |                          GITHUB_TOKEN pushes fire no push event:
  |                          push-to-obs rides workflow_run
  |
  o  PUSH-TO-OBS ............ syncs touched packages + vendor archives
  |
  o  OBS BUILDS ............. offline, from the vendored sources
  |
  o  BADGES ................ README + badges/*.json, ~1h20 after bump
  |                          blue ok - v->v building - red failed
  |
 (end of the pipeline)
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
