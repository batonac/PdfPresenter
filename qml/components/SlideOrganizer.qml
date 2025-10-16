import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root

    // Empty state
    Rectangle {
        anchors.centerIn: parent
        width: 400
        height: 200
        color: "white"
        radius: 8
        border.color: "#E1DFDD"
        border.width: 1
        visible: pdfBackend.slideCount === 0

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 40
            spacing: 16

            Text {
                text: "No slides loaded"
                font.pixelSize: 18
                font.bold: true
                color: "#1F1F1F"
                Layout.alignment: Qt.AlignHCenter
            }

            Text {
                text: "Drop PDF files here or use 'Import PDF' to get started"
                font.pixelSize: 13
                color: "#605E5C"
                Layout.alignment: Qt.AlignHCenter
                wrapMode: Text.WordWrap
                horizontalAlignment: Text.AlignHCenter
            }
        }
    }

    // Slide grid using Flow
    ScrollView {
        anchors.fill: parent
        anchors.bottomMargin: 50
        visible: pdfBackend.slideCount > 0
        clip: true
        
        Flow {
            id: slideGrid
            width: parent.width
            spacing: 20
            leftPadding: 20
            rightPadding: 20
            topPadding: 20
            bottomPadding: 20

            Repeater {
                model: pdfBackend.slideModel

                SlideThumbnail {
                    slideImage: model.slideImage
                    pageNumber: model.pageNumber
                    position: model.position
                    isSelected: pdfBackend.currentPage === model.position
                    
                    onClicked: {
                        pdfBackend.jumpToSlide(position)
                    }
                    
                    onDeleteClicked: {
                        pdfBackend.removeSlide(position)
                    }
                }
            }
        }
    }

    // Size control slider at bottom
    Rectangle {
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        height: 50
        color: "white"
        border.color: "#E1DFDD"
        border.width: 1

        RowLayout {
            anchors.fill: parent
            anchors.rightMargin: 20
            spacing: 8
            layoutDirection: Qt.RightToLeft

            Text {
                text: Math.round(sizeSlider.value) + "px"
                color: "#605E5C"
                font.pixelSize: 12
                Layout.preferredWidth: 50
            }

            Slider {
                id: sizeSlider
                from: 100
                to: 400
                value: 200
                stepSize: 10
                Layout.preferredWidth: 200
            }

            Text {
                text: "Thumbnail Size:"
                color: "#605E5C"
                font.pixelSize: 12
            }
        }
    }

    // Drop area for PDF files
    DropArea {
        anchors.fill: parent
        onDropped: (drop) => {
            if (drop.hasUrls) {
                var pdfFiles = []
                for (var i = 0; i < drop.urls.length; i++) {
                    var url = drop.urls[i].toString()
                    if (url.toLowerCase().endsWith('.pdf')) {
                        pdfFiles.push(url)
                    }
                }
                if (pdfFiles.length > 0) {
                    pdfBackend.importFiles(pdfFiles)
                }
            }
        }
    }
}
