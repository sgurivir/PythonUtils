mount -uw /

plutil -convert xml1 /System/Library/LaunchDaemons/com.apple.locationd.plist

defaults write /System/Library/LaunchDaemons/com.apple.locationd.plist  EnvironmentVariables -dict MallocStackLogging full
defaults write /System/Library/LaunchDaemons/com.apple.locationd.plist  EnvironmentVariables -dict DISPATCH_DEBUG_MISSING_POOLS YES
defaults write /System/Library/LaunchDaemons/com.apple.locationd.plist  EnvironmentVariables -dict OBJC_DEBUG_MISSING_POOLS YES
defaults write /System/Library/LaunchDaemons/com.apple.locationd.plist StandardErrorPath /private/var/tmp/locationd.err
defaults write /System/Library/LaunchDaemons/com.apple.locationd.plist StandardOutPath /private/var/tmp/locationd.out

launchctl unload /System/Library/LaunchDaemons/com.apple.locationd.plist
launchctl load /System/Library/LaunchDaemons/com.apple.locationd.plist


sysctl -w kern.memorystatus_highwater_enabled=0
jetsam_properties set Daemon Override com.apple.locationd InactiveHardMemoryLimit -1
jetsam_properties set Daemon Override com.apple.locationd ActiveSoftMemoryLimit -1

read -p "Needs Reboot. Press Enter to continue"
reboot

