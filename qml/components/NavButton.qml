import QtQuick
import QtQuick.Controls

Button {
    id: control
    
    Layout.fillWidth: true
    Layout.topMargin: 2
    height: 40

    background: Rectangle {
        color: control.hovered ? "#F5F5F5" : "transparent"
        radius: 4
        border.color: control.hovered ? "#E1DFDD" : "transparent"
        border.width: 1
    }

    contentItem: Text {
        text: control.text
        color: "#1F1F1F"
        font.pixelSize: 13
        horizontalAlignment: Text.AlignLeft
        verticalAlignment: Text.AlignVCenter
        leftPadding: 8
    }
}
