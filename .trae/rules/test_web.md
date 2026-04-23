- 每次修改后，等完成单元测试、整体测试后，推送到 github，后端部署完成后，自己完成测试看看部署和数据库能否正常运行并成功完成相应功能。
- 详细的测试逻辑和流程参考：`/TESTING_LOGIC_SUMMARY.md`

## Testing Documentation
- 完整测试逻辑总结：`/TESTING_LOGIC_SUMMARY.md`
  - 卖家流程（Seller Flow）
  - 买家流程（Buyer Flow）
  - 取消流程（Cancel Flow）
  - 消息系统（Messaging System）
  - 管理后台（Admin Dashboard）
- 部署问题分析：`/DEPLOYMENT_ISSUE_ANALYSIS.md`

## backend tests
- 推送到github上后，后端会自动部署，不用手动部署。
- 后端render api： rnd_PikBeUTpV99ai6DBbtI4ubTxeHTu
  - 后端render https://pku-campus-cycle-cycle.onrender.com
- render database： 
  - internal URL: postgresql://pku_cycle_db_qre8_user:xlZcWErBt7G5AVOq1ZjXLlv8v0K7v4wj@dpg-d7j3f3l7vvec73ahgetg-a/pku_cycle_db_qre8;
  - external URL: postgresql://pku_cycle_db_qre8_user:xlZcWErBt7G5AVOq1ZjXLlv8v0K7v4wj@dpg-d7j3f3l7vvec73ahgetg-a.oregon-postgres.render.com/pku_cycle_db_qre8
## Website tests
- Perform tests on the website https://pku-campus-cycle-cycle.vercel.app, testing the features of website after the success of deployment.
  - when testing the website, if an ordinary user does not exist, create it first and then test the features.
- supmin: 2200017736@stu.pku.edu.cn password: pkucycle