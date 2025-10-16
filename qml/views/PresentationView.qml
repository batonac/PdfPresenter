import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window

Window {
    id: presenterWindow
    width: 800
    height: 600
    title: "PDF Presenter - Presenter View"
    visible: false
    color: "#F3F3F3"

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

            // Preview card
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: "white"
                radius: 8
                border.color: "#E1DFDD"
                border.width: 1

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 12

                    Text {
                        text: "Current Slide"
                        font.pixelSize: 16
                        font.bold: true
                        color: "#1F1F1F"
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        color: "#F3F3F3"

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

            // Timer card
            Rectangle {
                Layout.preferredWidth: 200
                Layout.fillHeight: true
                color: "white"
                radius: 8
                border.color: "#E1DFDD"
                border.width: 1

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 12

                    Text {
                        text: "Timer"
                        font.pixelSize: 16
                        font.bold: true
                        color: "#1F1F1F"
                        Layout.alignment: Qt.AlignHCenter
                    }

                    Text {
                        text: pdfBackend.timerText
                        font.pixelSize: 36
                        font.bold: true
                        font.family: "monospace"
                        color: "#0078D4"
                        Layout.alignment: Qt.AlignHCenter
                    }

                    RowLayout {
                        Layout.alignment: Qt.AlignHCenter
                        spacing: 8

                        Button {
                            text: "Start"
                            onClicked: pdfBackend.startTimer()
                            
                            background: Rectangle {
                                color: parent.pressed ? "#005A9E" : (parent.hovered ? "#1084D8" : "#0078D4")
                                radius: 4
                            }
                            
                            contentItem: Text {
                                text: parent.text
                                color: "white"
                                font.pixelSize: 12
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                            }
                        }

                        Button {
                            text: "Stop"
                            onClicked: pdfBackend.stopTimer()
                            
                            background: Rectangle {
                                color: parent.hovered ? "#F3F3F3" : "white"
                                radius: 4
                                border.color: "#E1DFDD"
                                border.width: 1
                            }
                            
                            contentItem: Text {
                                text: parent.text
                                color: "#1F1F1F"
                                font.pixelSize: 12
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                            }
                        }
                    }
                }
            }
        }

        // Notes card
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "white"
            radius: 8
            border.color: "#E1DFDD"
            border.width: 1

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 12

                Text {
                    text: "Speaker Notes"
                    font.pixelSize: 16
                    font.bold: true
                    color: "#1F1F1F"
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
                        
                        background: Rectangle {
                            color: "transparent"
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
