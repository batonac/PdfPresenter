import QtQuick
import QtQuick.Controls.FluentWinUI3
import QtQuick.Layouts

Frame {
    id: root
    
    property var slideImage
    property int pageNumber
    property int position
    property bool isSelected: false
    
    signal clicked()
    signal deleteClicked()
    
    width: 224  // 200px thumbnail + 24px padding
    height: 324 // Calculated based on aspect ratio + controls
    
    ColumnLayout {
        anchors.fill: parent
        spacing: 8
        
        // Slide number
        Label {
            text: (position + 1).toString()
            font.pixelSize: 14
            font.bold: true
            Layout.alignment: Qt.AlignHCenter
        }
        
        // Thumbnail image
        Item {
            width: 200
            height: 282  // 200 * 1.41 aspect ratio
            Layout.preferredWidth: 200
            Layout.preferredHeight: 282
            
            Image {
                anchors.centerIn: parent
                width: parent.width
                height: parent.height
                source: slideImage ? "image://slideimage/" + position : ""
                fillMode: Image.PreserveAspectFit
                smooth: true
                cache: false
            }
        }
        
        // Delete button
        Button {
            text: "Delete"
            Layout.preferredWidth: 200
            Layout.alignment: Qt.AlignHCenter
            
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
}
