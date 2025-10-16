import QtQuick
import QtQuick.Controls.FluentWinUI3
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
        Pane {
            id: sidebar
            Layout.preferredWidth: 320
            Layout.fillHeight: true

            ColumnLayout {
                anchors.fill: parent
                spacing: 8

                // Header
                Label {
                    text: "PDF Presenter"
                    font.pixelSize: 20
                    font.bold: true
                    Layout.alignment: Qt.AlignHCenter
                    Layout.topMargin: 12
                    Layout.bottomMargin: 12
                }

                // Browse Folder button
                Button {
                    text: "📁 Browse Folder"
                    Layout.fillWidth: true
                    Layout.leftMargin: 8
                    Layout.rightMargin: 8
                    Layout.topMargin: 8
                    onClicked: folderDialog.open()
                }

                // File browser tree placeholder
                Frame {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 300
                    Layout.leftMargin: 8
                    Layout.rightMargin: 8
                    Layout.topMargin: 4

                    Label {
                        anchors.centerIn: parent
                        text: "File browser\n(to be implemented)"
                        horizontalAlignment: Text.AlignHCenter
                    }
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

                // Present button
                Button {
                    text: "▶️ Present"
                    Layout.fillWidth: true
                    Layout.leftMargin: 8
                    Layout.rightMargin: 8
                    Layout.topMargin: 8
                    Layout.bottomMargin: 8
                    enabled: pdfBackend.slideCount > 0
                    highlighted: true

                    onClicked: {
                        pdfBackend.presentationMode = true
                        presentationWindow.show()
                    }
                }
            }
        }

        // Main content area
        Pane {
            Layout.fillWidth: true
            Layout.fillHeight: true

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
