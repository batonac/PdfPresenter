import QtQuick
import QtQuick.Controls.FluentWinUI3
import QtQuick.Layouts
import QtQuick.Window

Window {
    id: presenterWindow
    width: 800
    height: 600
    title: "PDF Presenter - Presenter View"
    visible: false

    onVisibleChanged: {
        if (visible) {
            projectorWindow.show()
        } else {
            projectorWindow.close()
            pdfBackend.presentationMode = false
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 16

        // Top row: Preview and Timer
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 16

            // Preview pane
            Frame {
                Layout.fillWidth: true
                Layout.fillHeight: true

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 12

                    Label {
                        text: "Current Slide"
                        font.pixelSize: 16
                        font.bold: true
                    }

                    Item {
                        Layout.fillWidth: true
                        Layout.fillHeight: true

                        Image {
                            id: previewImage
                            anchors.centerIn: parent
                            width: Math.min(parent.width, 400)
                            height: Math.min(parent.height, 300)
                            fillMode: Image.PreserveAspectFit
                            smooth: true
                            
                            // Update on current page change
                            Connections {
                                target: pdfBackend
                                function onCurrentPageChanged() {
                                    // Trigger image update
                                    previewImage.source = ""
                                    previewImage.source = "image://thumbnail/" + pdfBackend.currentPage
                                }
                            }
                        }
                    }
                }
            }

            // Timer pane
            Frame {
                Layout.preferredWidth: 200
                Layout.fillHeight: true

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 12

                    Label {
                        text: "Timer"
                        font.pixelSize: 16
                        font.bold: true
                        Layout.alignment: Qt.AlignHCenter
                    }

                    Label {
                        text: pdfBackend.timerText
                        font.pixelSize: 36
                        font.bold: true
                        font.family: "monospace"
                        Layout.alignment: Qt.AlignHCenter
                    }

                    RowLayout {
                        Layout.alignment: Qt.AlignHCenter
                        spacing: 8

                        Button {
                            text: "Start"
                            highlighted: true
                            onClicked: pdfBackend.startTimer()
                        }

                        Button {
                            text: "Stop"
                            onClicked: pdfBackend.stopTimer()
                        }
                    }
                }
            }
        }

        // Notes pane
        Frame {
            Layout.fillWidth: true
            Layout.fillHeight: true

            ColumnLayout {
                anchors.fill: parent
                spacing: 12

                Label {
                    text: "Speaker Notes"
                    font.pixelSize: 16
                    font.bold: true
                }

                ScrollView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true

                    TextArea {
                        id: notesArea
                        text: pdfBackend.currentNotes
                        font.pixelSize: 14
                        wrapMode: TextArea.Wrap
                        selectByMouse: true
                        
                        onTextChanged: {
                            if (activeFocus) {
                                pdfBackend.currentNotes = text
                            }
                        }
                    }
                }
            }
        }
    }

    // Keyboard shortcuts
    Shortcut {
        sequence: "Left"
        onActivated: pdfBackend.prevSlide()
    }

    Shortcut {
        sequence: "Right"
        onActivated: pdfBackend.nextSlide()
    }

    Shortcut {
        sequence: "Ctrl+S"
        onActivated: pdfBackend.saveNotes()
    }

    Shortcut {
        sequence: "Escape"
        onActivated: presenterWindow.close()
    }

    Shortcut {
        sequence: "Q"
        onActivated: presenterWindow.close()
    }

    // Projector window
    Window {
        id: projectorWindow
        width: 640
        height: 480
        title: "PDF Presenter - Projection"
        visible: false
        color: "black"

        Image {
            id: projectionImage
            anchors.fill: parent
            fillMode: Image.PreserveAspectFit
            smooth: true
            
            // Update on current page change
            Connections {
                target: pdfBackend
                function onCurrentPageChanged() {
                    // Trigger image update
                    projectionImage.source = ""
                    projectionImage.source = "image://projection/" + pdfBackend.currentPage
                }
            }
        }

        // Keyboard shortcuts for projector window
        Shortcut {
            sequence: "F11"
            onActivated: {
                if (projectorWindow.visibility === Window.FullScreen) {
                    projectorWindow.visibility = Window.Windowed
                } else {
                    projectorWindow.visibility = Window.FullScreen
                }
            }
        }

        Shortcut {
            sequence: "F"
            onActivated: {
                if (projectorWindow.visibility === Window.FullScreen) {
                    projectorWindow.visibility = Window.Windowed
                } else {
                    projectorWindow.visibility = Window.FullScreen
                }
            }
        }

        Shortcut {
            sequence: "Escape"
            onActivated: presenterWindow.close()
        }

        Shortcut {
            sequence: "Q"
            onActivated: presenterWindow.close()
        }

        Shortcut {
            sequence: "Left"
            onActivated: pdfBackend.prevSlide()
        }

        Shortcut {
            sequence: "Right"
            onActivated: pdfBackend.nextSlide()
        }
    }
}
