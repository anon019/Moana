/**
 * 海报生成工具
 * 使用 Canvas 生成分享海报图片
 */

export interface PosterData {
  title: string
  coverUrl: string
  childName: string
  theme: string
}

/**
 * 下载图片到本地临时路径
 */
async function downloadImage(url: string): Promise<string> {
  return new Promise((resolve, reject) => {
    // 处理 http -> https
    let safeUrl = url
    if (safeUrl.startsWith('http://')) {
      safeUrl = safeUrl.replace('http://', 'https://')
    }

    uni.downloadFile({
      url: safeUrl,
      success: (res) => {
        if (res.statusCode === 200) {
          resolve(res.tempFilePath)
        } else {
          reject(new Error('图片下载失败'))
        }
      },
      fail: reject
    })
  })
}

/**
 * 绘制圆角矩形
 */
function drawRoundRect(
  ctx: UniApp.CanvasContext,
  x: number,
  y: number,
  width: number,
  height: number,
  radius: number
) {
  ctx.beginPath()
  ctx.moveTo(x + radius, y)
  ctx.lineTo(x + width - radius, y)
  ctx.arcTo(x + width, y, x + width, y + radius, radius)
  ctx.lineTo(x + width, y + height - radius)
  ctx.arcTo(x + width, y + height, x + width - radius, y + height, radius)
  ctx.lineTo(x + radius, y + height)
  ctx.arcTo(x, y + height, x, y + height - radius, radius)
  ctx.lineTo(x, y + radius)
  ctx.arcTo(x, y, x + radius, y, radius)
  ctx.closePath()
}

/**
 * 生成分享海报
 * @param canvasId Canvas ID
 * @param data 海报数据
 * @param context 组件实例（用于 canvas 作用域）
 * @returns 海报图片临时路径
 */
export async function generatePoster(
  canvasId: string,
  data: PosterData,
  context: any
): Promise<string> {
  const ctx = uni.createCanvasContext(canvasId, context)
  const width = 540
  const height = 960

  // 1. 背景 - 温暖奶油色
  ctx.setFillStyle('#FFF9F5')
  ctx.fillRect(0, 0, width, height)

  // 2. 顶部装饰条
  ctx.setFillStyle('#FF7B54')
  ctx.fillRect(0, 0, width, 80)

  // 3. 标题
  ctx.setFillStyle('#FFFFFF')
  ctx.setFontSize(32)
  ctx.setTextAlign('center')
  ctx.fillText('童话绘本', width / 2, 52)

  // 4. 封面图
  try {
    const coverPath = await downloadImage(data.coverUrl)
    // 绘制圆角封面背景
    ctx.save()
    drawRoundRect(ctx, 40, 120, width - 80, 400, 16)
    ctx.clip()
    ctx.drawImage(coverPath, 40, 120, width - 80, 400)
    ctx.restore()
  } catch (e) {
    // 封面加载失败，绘制占位
    ctx.save()
    drawRoundRect(ctx, 40, 120, width - 80, 400, 16)
    ctx.setFillStyle('#FFE4D6')
    ctx.fill()
    ctx.restore()

    // 占位图标
    ctx.setFillStyle('#FF7B54')
    ctx.setFontSize(80)
    ctx.setTextAlign('center')
    ctx.fillText('📚', width / 2, 340)
  }

  // 5. 绘本标题
  ctx.setFillStyle('#3D2914')
  ctx.setFontSize(36)
  ctx.setTextAlign('center')
  // 标题过长时截断
  let displayTitle = data.title
  if (displayTitle.length > 12) {
    displayTitle = displayTitle.substring(0, 12) + '...'
  }
  ctx.fillText(displayTitle, width / 2, 580)

  // 6. 主题标签
  if (data.theme) {
    ctx.setFillStyle('#FF7B54')
    ctx.setFontSize(24)
    ctx.fillText(`#${data.theme}`, width / 2, 630)
  }

  // 7. 孩子名字
  ctx.setFillStyle('#9C8578')
  ctx.setFontSize(28)
  ctx.fillText(`${data.childName} 的专属绘本`, width / 2, 700)

  // 8. 装饰分隔线
  ctx.setStrokeStyle('#FFE4D6')
  ctx.setLineWidth(2)
  ctx.beginPath()
  ctx.moveTo(120, 760)
  ctx.lineTo(width - 120, 760)
  ctx.stroke()

  // 9. 小程序名称
  ctx.setFillStyle('#FF7B54')
  ctx.setFontSize(28)
  ctx.fillText('Moana 童话绘本', width / 2, 820)

  // 10. 底部提示
  ctx.setFillStyle('#C4B5A9')
  ctx.setFontSize(22)
  ctx.fillText('长按识别小程序码，创作专属绘本', width / 2, 900)

  // 绘制并导出
  return new Promise((resolve, reject) => {
    ctx.draw(false, () => {
      setTimeout(() => {
        uni.canvasToTempFilePath({
          canvasId,
          success: (res) => resolve(res.tempFilePath),
          fail: reject
        }, context)
      }, 100) // 等待绘制完成
    })
  })
}

/**
 * 保存图片到相册
 */
export async function savePosterToAlbum(filePath: string): Promise<void> {
  return new Promise((resolve, reject) => {
    uni.saveImageToPhotosAlbum({
      filePath,
      success: () => resolve(),
      fail: (err) => {
        // 检查是否是权限问题
        if (err.errMsg?.includes('auth deny') || err.errMsg?.includes('authorize')) {
          uni.showModal({
            title: '需要相册权限',
            content: '请在设置中允许访问相册，以保存海报图片',
            confirmText: '去设置',
            success: (res) => {
              if (res.confirm) {
                uni.openSetting({})
              }
            }
          })
        }
        reject(err)
      }
    })
  })
}
