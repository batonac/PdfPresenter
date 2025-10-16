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

        FlexboxLayout {
            anchors.fill: parent
            anchors.margins: 40
            flow: FlexboxLayout.TopToBottom
            justifyContent: FlexboxLayout.JustifyCenter
            alignItems: FlexboxLayout.AlignCenter

            Text {
                text: "No slides loaded"
                font.pixelSize: 18
                font.bold: true
                color: "#1F1F1F"
                Layout.alignment: FlexboxLayout.AlignHCenter
            }

            Text {
                text: "Drop PDF files here or use 'Import PDF' to get started"
                font.pixelSize: 13
                color: "#605E5C"
                Layout.alignment: FlexboxLayout.AlignHCenter
                Layout.topMargin: 8
                wrapMode: Text.WordWrap
                horizontalAlignment: Text.AlignHCenter
            }
        }
    }

    // Slide grid with FlexboxLayout
    ScrollView {
        anchors.fill: parent
        visible: pdfBackend.slideCount > 0
        clip: true
        
        FlexboxLayout {
            id: slideGrid
            width: parent.width
            flow: FlexboxLayout.LeftToRight
            wrap: FlexboxLayout.Wrap
            justifyContent: FlexboxLayout.JustifyStart
            padding: 20
            columnGap: 20
            rowGap: 20

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

        FlexboxLayout {
            anchors.fill: parent
            anchors.rightMargin: 20
            flow: FlexboxLayout.LeftToRight
            justifyContent: FlexboxLayout.JustifyEnd
            alignItems: FlexboxLayout.AlignCenter

            Text {
                text: "Thumbnail Size:"
                color: "#605E5C"
                font.pixelSize: 12
                Layout.rightMargin: 8
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
                text: Math.round(sizeSlider.value) + "px"
                color: "#605E5C"
                font.pixelSize: 12
                Layout.preferredWidth: 50
                Layout.leftMargin: 8
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
