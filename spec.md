# 产品规格说明书：燕园易骑 (PKU Cycle-Recycle Hub)

## 1. 项目概述
**燕园易骑 (PKU Cycle-Recycle Hub)** 是一个校园自行车循环回收平台，旨在解决北京大学校园内废旧自行车堆积的问题。它将连接即将毕业离校的学生（需要处置自行车）和新生或其他师生（需要低廉的代步工具）。

该平台将是一个公开访问的 Web 应用，具有持久且免费的云端存储（用于数据和图片），并支持实时匹配和库存状态跟踪。

## 2. 目标用户
* **供应方 (卖家/捐赠者)：** 即将毕业离校的学生。
* **需求方 (买家)：** 刚入学的新生及校内其他有代步需求的师生。
* **管理员 (Admin)：** 负责线下车辆存放、成色鉴定及核销的学生志愿者或校园管理人员。
* **主负责人 (SuperAdmin)：** 项目的核心管理者，拥有指派或移除管理员的最高权限。

## 3. 用户角色与权限 (Roles & Permissions)
* **普通用户 (User):**
  - 注册、登录（邮箱+密码）。
  - 发布自行车（等待管理员审核）。
  - 浏览已审核通过的自行车库存。
  - 预约（锁定）在库自行车。
  - 在个人中心查看自己的发布、预约记录。
  - 在社区论坛发帖、评论、点赞。
* **管理员 (Admin):**
  - 拥有普通用户所有权限。
  - 审核用户发布的自行车，批准或驳回。
  - 管理所有自行车的状态（如手动下架、确认交易完成）。
  - 设置可供线下交易的时间段。
  - 在管理后台查看所有用户、车辆和交易记录。
* **主负责人 (SuperAdmin):**
  - 拥有管理员所有权限。
  - 添加或移除管理员账号。
  - **初始账号**: 邮箱 `2200017736@stu.pku.edu.cn`，密码 `pkucycle`。
  - 可将 SuperAdmin 权限转让给其他用户。

## 4. 核心功能 (Core Features)
### 4.1 门户与宣传模块
* **核心入口：** 清晰的"捐赠/出售"与"寻找座驾"两个主要按钮。
* **项目愿景展示：** 实时展示回收数据（例如：已累计回收多少辆自行车，减少了多少千克金属浪费）。

### 4.2 车辆回收模块 (供应方)
* **车辆登记：** 毕业生上传照片，填写品牌、新旧程度（评分制），以及意向价格（可选择"免费捐赠"）。车辆初始状态为 **"待审核"**。
* **管理员审核：** 管理员在后台审核车辆信息，可以：
  - 拒绝交易并给出理由（通知卖家）
  - 提出若干（>=1）个管理员有空闲的时间段
* **卖家选择时间段：** 卖家收到通知，从管理员提供的时间段中选择一个（使用日历时间选择器）
* **管理员确认：** 管理员确认卖家选择的时间段，通知卖家
* **线下交易：** 双方进行线下交易
* **交易完成：** 管理员确认交易，自行车入库；卖家收到提醒，可以进行评价
* **取消交易：** 在登记到线下交易的时间段内，卖家随时可以取消交易，管理员也可以随时拒绝交易并给出理由
* **更改时间段：** 在管理员提出时间段后到进行线下交易前，管理员可以更改时间段，重新通知用户

### 4.3 智能匹配与抢先预约 (需求方)
* **搜索与筛选：** 用户可根据期望的价位、成色范围筛选合适的自行车。
* **实时库存：** 用户浏览时，若某车辆已被他人预览或预订，系统将实时更新状态以避免冲突。
* **预约流程：**
  1. 用户选择心仪车辆后创建预约申请，车辆状态变为 **"锁定中 (Locked)"**
  2. 管理员查看预约申请，可以：
     - 拒绝交易并给出理由（通知买家）
     - 提出若干（>=1）个管理员有空闲的时间段
  3. 买家从管理员提供的时间段中选择一个（使用日历时间选择器），确认预约时间
  4. 管理员确认买家选择的时间段
  5. 线下提车/交付
  6. 管理员确认提车完成，车辆状态更新为 SOLD
  7. 买家收到提醒，可以对服务进行评价
* **取消与更改：**
  - 买家可以随时取消预约（在交易完成前）
  - 管理员可以随时拒绝交易并给出理由
  - 在管理员提出时间段后到进行线下交易前，管理员可以更改时间段，重新通知用户
* **防冲突机制：** 如果两名学生同时抢订同一辆车，系统将锁定给首位操作者，并提示另一名用户重新选择。

### 4.4 时间段管理系统
* **管理员设置时间段：** 管理员可以为特定预约创建多个可选时间段（开始时间、结束时间）
* **用户选择时间段：** 用户从管理员提供的可用时间段中选择一个
* **时间段状态：** 每个时间段有"未预订"和"已预订"两种状态
* **预约类型：** 支持"drop-off"（卖家交车）和"pick-up"（买家提车）两种类型

### 4.5 评价系统
* **买家评价：** 买家提车后可以作为买家对服务进行评价（1-5 星 + 文字评论）
* **卖家评价：** 卖家交车后可以作为卖家对服务进行评价（1-5 星 + 文字评论）
* **评价展示：** 评价记录保存在数据库中，未来可在个人中心查看

### 4.6 社区反馈模块 (论坛)
* **帖子列表：** 用户可发布对项目的建议、使用心得或问题，形成帖子。
* **互动功能：** 其他用户可以对帖子进行 **评论** 和 **点赞**。
* **删除功能：** 发帖人可以删除自己的帖子和评论。

### 4.7 私信系统
* **管理员与用户私信：** 管理员可以主动联系卖家或买家，用户也可以联系所有管理员
* **用户间私信：** 卖家和买家之间可以互相发送私信
* **留言形式：** 私信以留言形式保存，非实时聊天
* **查看方式：** 在个人中心查看私信记录，支持查看已读/未读状态
* **通知功能：** 收到新私信时，用户会收到通知提醒

### 4.8 主页增强模块
* **交易倒计时：** 在主页增加一个模块，用户和管理员如果已经选择了时间段，可以在模块中显示还有多少时间进行交易；若还未选择时间段，则只显示有未完成的交易
* **平台使用说明：** 详细介绍平台的使用流程和步骤
* **宣传展示：** 展示项目的愿景、环保理念和已回收的自行车数量
* **数据统计：** 实时显示已交易自行车数量（与数据库同步）

### 4.5 个人中心与管理后台
* **个人中心 (用户视图):**
  - **我的发布:** 查看自己发布的车辆状态（待审核/已入库/已售出）。
  - **我的预约:** 查看已预约车辆的匹配进度和历史交易记录。
  - **账号设置:** 修改密码、查看个人角色。
* **管理后台 (管理员/主负责人视图):**
  - **用户管理:** (SuperAdmin) 添加/移除管理员，或将 SuperAdmin 权限转让。
  - **车辆管理:** 审核新提交的车辆、管理所有车辆信息。
  - **预约管理:** 查看和管理所有用户的预约时间段。
  - **数据看板:** 查看平台所有历史交易记录和统计数据。

## 5. 技术方案 (免费部署)

### 5.1 技术栈
* **前端框架:** **Next.js 16 (React)**，利用 App Router 和 Server Actions。
* **UI 与样式:** **Tailwind CSS**，现代化、简洁的界面。
* **后端框架:** **FastAPI**，高性能 Python Web 框架。
* **数据库:** **Supabase** PostgreSQL（免费 500MB 存储）。
* **存储:** **Supabase Storage**（用于存放自行车照片）。

### 5.2 部署方案
* **前端部署:** **Vercel**（免费无缝部署 Next.js 应用）。
* **后端部署:** **Railway** 或 **Render**（免费容器托管 FastAPI 应用）。
  - Railway: 每月 500 小时免费额度，活动时更多。
  - Render: 每月 750 小时免费额度。
* **数据库:** **Supabase**（免费云数据库，即用即启动）。

### 5.3 环境变量配置
```
# Backend (.env)
DATABASE_URL=postgresql://xxx.supabase.co:5432/postgres
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your-anon-key
SECRET_KEY=your-jwt-secret-key

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

## 6. 数据库模型 (Supabase PostgreSQL)

### 6.1 Users 表
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100),
    role VARCHAR(20) DEFAULT 'USER' CHECK (role IN ('USER', 'ADMIN', 'SUPER_ADMIN')),
    avatar_url TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 6.2 Bicycles 表
```sql
CREATE TABLE bicycles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID REFERENCES users(id),
    brand VARCHAR(100) NOT NULL,
    condition INTEGER CHECK (condition >= 1 AND condition <= 10),
    price DECIMAL(10, 2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'PENDING_APPROVAL' CHECK (status IN ('PENDING_APPROVAL', 'IN_STOCK', 'LOCKED', 'SOLD')),
    image_url TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 6.3 Appointments 表
```sql
CREATE TABLE appointments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    bicycle_id UUID REFERENCES bicycles(id),
    type VARCHAR(20) CHECK (type IN ('drop-off', 'pick-up')),
    status VARCHAR(20) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'CONFIRMED', 'COMPLETED', 'CANCELLED')),
    time_slot_id UUID REFERENCES time_slots(id),
    appointment_time TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 6.4 TimeSlots 表
```sql
CREATE TABLE time_slots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bicycle_id UUID REFERENCES bicycles(id),
    appointment_type VARCHAR(20) CHECK (appointment_type IN ('drop-off', 'pick-up')),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    is_booked VARCHAR(10) DEFAULT 'false',
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 6.5 Reviews 表
```sql
CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    appointment_id UUID REFERENCES appointments(id),
    reviewer_id UUID REFERENCES users(id),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    content TEXT,
    review_type VARCHAR(20) CHECK (review_type IN ('buyer_review', 'seller_review')),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 6.6 Posts 表
```sql
CREATE TABLE posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    author_id UUID REFERENCES users(id),
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 6.7 Comments 表
```sql
CREATE TABLE comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
    author_id UUID REFERENCES users(id),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 6.8 Likes 表
```sql
CREATE TABLE likes (
    post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (post_id, user_id)
);
```

## 7. API 设计

### 7.1 认证接口
* `POST /auth/register` - 用户注册（邮箱+密码）
* `POST /auth/login` - 用户登录，返回 JWT token
* `POST /auth/logout` - 登出
* `GET /auth/me` - 获取当前用户信息

### 7.2 用户管理接口
* `GET /users/` - 获取所有用户（Admin/SuperAdmin）
* `PUT /users/{user_id}/role` - 修改用户角色（SuperAdmin）
* `GET /users/{user_id}` - 获取指定用户信息

### 7.3 自行车管理接口
* `POST /bicycles/` - 创建自行车（需认证）
* `GET /bicycles/` - 获取自行车列表（支持筛选）
* `GET /bicycles/{bike_id}` - 获取自行车详情
* `PUT /bicycles/{bike_id}` - 更新自行车信息
* `PUT /bicycles/{bike_id}/approve` - 审核自行车（Admin）
* `DELETE /bicycles/{bike_id}` - 删除自行车

### 7.4 预约管理接口
* `POST /appointments/` - 创建预约
* `GET /appointments/` - 获取所有预约（管理员）/ 用户自己的预约（普通用户）
* `GET /appointments/user/{user_id}` - 获取用户预约
* `PUT /appointments/{apt_id}` - 更新预约状态
* `POST /time_slots/` - 创建时间段（管理员）
* `GET /time_slots/appointment/{apt_id}` - 获取预约的可选时间段
* `PUT /appointments/{apt_id}/select-slot` - 用户选择时间段
* `PUT /appointments/{apt_id}/confirm-pickup` - 管理员确认提车
* `POST /reviews/` - 创建评价

### 7.5 论坛接口
* `POST /posts/` - 创建帖子
* `GET /posts/` - 获取帖子列表
* `GET /posts/{post_id}` - 获取帖子详情
* `PUT /posts/{post_id}` - 更新帖子
* `DELETE /posts/{post_id}` - 删除帖子（作者或管理员）
* `POST /posts/{post_id}/comments` - 添加评论
* `GET /posts/{post_id}/comments` - 获取帖子评论列表
* `DELETE /posts/{post_id}/comments/{comment_id}` - 删除评论（作者或管理员）
* `POST /posts/{post_id}/likes` - 点赞/取消点赞

## 8. UI/UX 设计规范

### 8.1 视觉风格
* **主题色:** 环保绿 (Eco Green) `#1f874c` / `#2ab26a`
* **风格方向:** 亲和卡通/插画风，轻松友好
* **卡片设计:** 大卡片精细化展示，不采用拥挤的瀑布流
* **背景美化:** 使用自行车/校园相关的图片作为页面背景，配合 SVG 插画装饰
* **时间段选择器:** 使用日历和时间选择器组件，用户可以在日历上直观选择日期和时间

### 8.2 页面结构
* `/` - 首页（入口 + 数据展示 + 交易倒计时）
* `/bicycles` - 自行车库存浏览
* `/bicycles/new` - 发布新自行车
* `/profile` - 个人中心（包含私信功能）
* `/forum` - 社区广场
* `/admin` - 管理后台
* `/login` - 登录页
* `/register` - 注册页

## 9. 开发阶段规划

### Phase 1: 基础设施（已完成部分）
- [x] Next.js 前端项目搭建
- [x] FastAPI 后端框架
- [x] 基础页面路由
- [x] 内存数据库（测试用）

### Phase 2: 核心功能（本阶段目标）
- [ ] Supabase 项目创建和数据库配置
- [ ] 用户认证系统（注册/登录/JWT）
- [ ] 角色权限系统（User/Admin/SuperAdmin）
- [ ] 持久化数据层
- [ ] 前端登录/注册页面

### Phase 3: 业务功能
- [ ] 自行车 CRUD + 审核流程
- [ ] 预约管理
- [ ] 论坛功能（帖子/评论/点赞）
- [ ] 管理后台完善

### Phase 4: 部署上线
- [ ] Vercel 前端部署
- [ ] Railway/Render 后端部署
- [ ] 域名绑定（如需要）
