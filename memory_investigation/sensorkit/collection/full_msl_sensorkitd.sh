mount -uw /

plutil -convert xml1 /System/Library/LaunchDaemons/com.apple.sensorkitd.plist

sysctl -w kern.memorystatus_highwater_enabled=0
jetsam_properties set Daemon Override com.apple.sensorkitd InactiveHardMemoryLimit -1
jetsam_properties set Daemon Override com.apple.sensorkitd ActiveSoftMemoryLimit -1

defaults write /System/Library/LaunchDaemons/com.apple.sensorkitd.plist  EnvironmentVariables -dict MallocStackLogging full
launchctl unload /System/Library/LaunchDaemons/com.apple.sensorkitd.plist
launchctl load /System/Library/LaunchDaemons/com.apple.sensorkitd.plist

read -p "Needs Reboot. Press Enter to continue"
reboot

