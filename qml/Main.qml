import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import "components"
import "views"

ApplicationWindow {
    id: root
    visible: true
    width: 1200
    height: 700
    title: "PDF Presenter"

    // Modern color palette inspired by FluentWinUI3
    readonly property color backgroundColor: "#F3F3F3"
    readonly property color cardColor: "#FFFFFF"
    readonly property color accentColor: "#0078D4"
    readonly property color textColor: "#1F1F1F"
    readonly property color subtleTextColor: "#605E5C"
    readonly property color hoverColor: "#F5F5F5"
    readonly property color borderColor: "#E1DFDD"

    background: Rectangle {
        color: root.backgroundColor
    }

    Component.onCompleted: {
        // Initialize presentation mode to false
        pdfBackend.presentationMode = false
    }

    // Main content area using RowLayout
    RowLayout {
        id: mainLayout
        anchors.fill: parent
        spacing: 0

        // Navigation sidebar
        Rectangle {
            id: sidebar
            Layout.preferredWidth: 320
            Layout.fillHeight: true
            color: root.cardColor
            
            Rectangle {
                anchors.right: parent.right
                width: 1
                height: parent.height
                color: root.borderColor
            }

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 8
                spacing: 8

                // Header
                Text {
                    text: "PDF Presenter"
                    font.pixelSize: 20
                    font.bold: true
                    color: root.textColor
                    Layout.alignment: Qt.AlignHCenter
                    Layout.topMargin: 12
                    Layout.bottomMargin: 12
                }

                Rectangle {
                    Layout.preferredHeight: 1
                    Layout.fillWidth: true
                    color: root.borderColor
                }

                // Browse Folder button
                Button {
                    text: "📁 Browse Folder"
                    Layout.fillWidth: true
                    Layout.leftMargin: 8
                    Layout.rightMargin: 8
                    Layout.topMargin: 8
                    onClicked: folderDialog.open()
                    
                    background: Rectangle {
                        color: parent.hovered ? root.hoverColor : "transparent"
                        radius: 4
                        border.color: root.borderColor
                        border.width: parent.hovered ? 1 : 0
                    }
                }

                // File browser tree placeholder
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 300
                    Layout.leftMargin: 8
                    Layout.rightMargin: 8
                    Layout.topMargin: 4
                    color: "transparent"
                    border.color: root.borderColor
                    border.width: 1
                    radius: 6

                    Text {
                        anchors.centerIn: parent
                        text: "File browser\n(to be implemented)"
                        color: root.subtleTextColor
                        horizontalAlignment: Text.AlignHCenter
                    }
                }

                Rectangle {
                    Layout.preferredHeight: 1
                    Layout.fillWidth: true
                    color: root.borderColor
                    Layout.topMargin: 8
                }

                // Actions
                ColumnLayout {
                    Layout.fillWidth: true
                    Layout.leftMargin: 8
                    Layout.rightMargin: 8
                    Layout.topMargin: 8
                    spacing: 2

                    NavButton {
                        text: "➕ Import PDF"
                        onClicked: fileDialog.open()
                    }

                    NavButton {
                        text: "💾 Export PDF"
                        onClicked: exportDialog.open()
                    }

                    NavButton {
                        text: "🗑️ Remove Page"
                        onClicked: {
                            // Remove currently selected page (needs to track selection)
                            if (pdfBackend.currentPage >= 0) {
                                pdfBackend.removeSlide(pdfBackend.currentPage)
                            }
                        }
                    }
                }

                // Spacer
                Item {
                    Layout.fillHeight: true
                }

                Rectangle {
                    Layout.preferredHeight: 1
                    Layout.fillWidth: true
                    color: root.borderColor
                }

                // Present button
                Button {
                    text: "▶️ Present"
                    Layout.fillWidth: true
                    Layout.leftMargin: 8
                    Layout.rightMargin: 8
                    Layout.topMargin: 8
                    Layout.bottomMargin: 8
                    enabled: pdfBackend.slideCount > 0

                    background: Rectangle {
                        color: parent.enabled ? (parent.pressed ? "#005A9E" : (parent.hovered ? "#1084D8" : root.accentColor)) : "#CCCCCC"
                        radius: 4
                    }

                    contentItem: Text {
                        text: parent.text
                        color: "white"
                        font.pixelSize: 14
                        font.bold: true
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }

                    onClicked: {
                        pdfBackend.presentationMode = true
                        presentationWindow.show()
                    }
                }
            }
        }

        // Main content area
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: root.backgroundColor

            SlideOrganizer {
                id: slideOrganizer
                anchors.fill: parent
                visible: !pdfBackend.presentationMode
            }
        }
    }

    // Dialogs
    FolderDialog {
        id: folderDialog
        title: "Select Folder"
        onAccepted: {
            // Handle folder selection
            console.log("Selected folder:", selectedFolder)
        }
    }

    FileDialog {
        id: fileDialog
        title: "Import PDF"
        nameFilters: ["PDF files (*.pdf)"]
        onAccepted: {
            pdfBackend.importFile(selectedFile.toString())
        }
    }

    FileDialog {
        id: exportDialog
        title: "Export PDF"
        fileMode: FileDialog.SaveFile
        nameFilters: ["PDF files (*.pdf)"]
        defaultSuffix: "pdf"
        onAccepted: {
            pdfBackend.exportPDF(selectedFile.toString())
        }
    }

    // Presentation window
    PresentationView {
        id: presentationWindow
        visible: false
    }

    // Message dialog for errors
    Dialog {
        id: errorDialog
        property string errorTitle: ""
        property string errorMessage: ""
        
        title: errorTitle
        modal: true
        anchors.centerIn: parent
        
        contentItem: Text {
            text: errorDialog.errorMessage
            wrapMode: Text.Wrap
        }
        
        standardButtons: Dialog.Ok
    }

    Connections {
        target: pdfBackend
        function onErrorOccurred(title, message) {
            errorDialog.errorTitle = title
            errorDialog.errorMessage = message
            errorDialog.open()
        }
    }
}
