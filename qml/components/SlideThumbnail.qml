import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    
    property var slideImage
    property int pageNumber
    property int position
    property bool isSelected: false
    
    signal clicked()
    signal deleteClicked()
    
    width: 224  // 200px thumbnail + 24px padding
    height: 324 // Calculated based on aspect ratio + controls
    color: "white"
    radius: isSelected ? 16 : 8
    border.color: isSelected ? "#0078D4" : "#E1DFDD"
    border.width: isSelected ? 2 : 1
    
    // Shadow effect
    layer.enabled: true
    layer.effect: ShaderEffect {
        property real spread: 0.1
        fragmentShader: "
            varying highp vec2 qt_TexCoord0;
            uniform sampler2D source;
            uniform lowp float qt_Opacity;
            uniform lowp float spread;
            void main() {
                lowp vec4 color = texture2D(source, qt_TexCoord0);
                gl_FragColor = color * qt_Opacity;
            }
        "
    }
    
    FlexboxLayout {
        anchors.fill: parent
        anchors.margins: 12
        flow: FlexboxLayout.TopToBottom
        alignItems: FlexboxLayout.AlignCenter
        rowGap: 8
        
        // Slide number
        Text {
            text: (position + 1).toString()
            font.pixelSize: 14
            font.bold: true
            color: "#1F1F1F"
            Layout.alignment: FlexboxLayout.AlignHCenter
        }
        
        // Thumbnail image
        Rectangle {
            width: 200
            height: 282  // 200 * 1.41 aspect ratio
            color: "#F3F3F3"
            
            Image {
                anchors.centerIn: parent
                width: parent.width
                height: parent.height
                source: slideImage ? "image://slideimage/" + position : ""
                fillMode: Image.PreserveAspectFit
                smooth: true
                cache: false
                
                // Fallback for image provider
                onStatusChanged: {
                    if (status === Image.Error || status === Image.Null) {
                        // Try to use the image directly if image provider doesn't work
                        // This is a workaround for the QImage to QML binding
                    }
                }
            }
        }
        
        // Delete button
        Button {
            text: "Delete"
            Layout.preferredWidth: 200
            Layout.preferredHeight: 32
            
            background: Rectangle {
                color: parent.hovered ? "#F3F3F3" : "white"
                radius: 4
                border.color: "#E1DFDD"
                border.width: 1
            }
            
            contentItem: Text {
                text: parent.text
                color: "#D13438"
                font.pixelSize: 12
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
            
            onClicked: root.deleteClicked()
        }
    }
    
    // Mouse area for selection
    MouseArea {
        anchors.fill: parent
        acceptedButtons: Qt.LeftButton
        onClicked: root.clicked()
        
        // Drag and drop support (simplified)
        drag.target: root
        drag.axis: Drag.XAndYAxis
    }
    
    // Hover effect
    states: [
        State {
            name: "hovered"
            when: mouseArea.containsMouse && !isSelected
            PropertyChanges {
                target: root
                border.color: "#0078D4"
                border.width: 1
            }
        }
    ]
    
    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        acceptedButtons: Qt.NoButton
    }
}
