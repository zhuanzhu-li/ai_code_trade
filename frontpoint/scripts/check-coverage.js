#!/usr/bin/env node
/**
 * 覆盖率检查脚本
 * 检查测试覆盖率是否达到指定阈值
 */

const fs = require('fs');
const path = require('path');

// 默认阈值50%
const THRESHOLD = process.argv[2] ? parseInt(process.argv[2]) : 50;

console.log('🔍 检查测试覆盖率...');

// 检查覆盖率文件是否存在
const coverageFile = path.join(__dirname, '..', 'coverage', 'coverage-final.json');
if (!fs.existsSync(coverageFile)) {
    console.error('❌ 覆盖率文件不存在:', coverageFile);
    process.exit(1);
}

try {
    // 读取覆盖率JSON文件
    const coverageData = JSON.parse(fs.readFileSync(coverageFile, 'utf8'));
    
    // 计算总体覆盖率
    let totalStatements = 0;
    let coveredStatements = 0;
    let totalBranches = 0;
    let coveredBranches = 0;
    let totalFunctions = 0;
    let coveredFunctions = 0;
    let totalLines = 0;
    let coveredLines = 0;
    
    // 遍历所有文件计算覆盖率
    for (const filePath in coverageData) {
        const fileData = coverageData[filePath];
        
        // 统计语句覆盖率
        if (fileData.s) {
            for (const statement in fileData.s) {
                totalStatements++;
                if (fileData.s[statement] > 0) {
                    coveredStatements++;
                }
            }
        }
        
        // 统计分支覆盖率
        if (fileData.b) {
            for (const branch in fileData.b) {
                totalBranches++;
                if (fileData.b[branch] > 0) {
                    coveredBranches++;
                }
            }
        }
        
        // 统计函数覆盖率
        if (fileData.f) {
            for (const func in fileData.f) {
                totalFunctions++;
                if (fileData.f[func] > 0) {
                    coveredFunctions++;
                }
            }
        }
        
        // 统计行覆盖率
        if (fileData.l) {
            for (const line in fileData.l) {
                totalLines++;
                if (fileData.l[line] > 0) {
                    coveredLines++;
                }
            }
        }
    }
    
    // 计算百分比
    const statementCoverage = totalStatements > 0 ? Math.round((coveredStatements / totalStatements) * 100 * 100) / 100 : 0;
    const branchCoverage = totalBranches > 0 ? Math.round((coveredBranches / totalBranches) * 100 * 100) / 100 : 0;
    const functionCoverage = totalFunctions > 0 ? Math.round((coveredFunctions / totalFunctions) * 100 * 100) / 100 : 0;
    const lineCoverage = totalLines > 0 ? Math.round((coveredLines / totalLines) * 100 * 100) / 100 : 0;
    
    // 计算平均覆盖率
    const averageCoverage = Math.round((statementCoverage + branchCoverage + functionCoverage + lineCoverage) / 4 * 100) / 100;
    
    // 显示覆盖率信息
    console.log('📊 覆盖率报告:');
    console.log(`   语句覆盖率: ${statementCoverage}% (${coveredStatements}/${totalStatements})`);
    console.log(`   分支覆盖率: ${branchCoverage}% (${coveredBranches}/${totalBranches})`);
    console.log(`   函数覆盖率: ${functionCoverage}% (${coveredFunctions}/${totalFunctions})`);
    console.log(`   行覆盖率: ${lineCoverage}% (${coveredLines}/${totalLines})`);
    console.log(`   平均覆盖率: ${averageCoverage}%`);
    
    // 检查是否达到阈值
    if (averageCoverage >= THRESHOLD) {
        console.log(`✅ 覆盖率检查通过！平均覆盖率 ${averageCoverage}% >= ${THRESHOLD}%`);
        process.exit(0);
    } else {
        console.log(`❌ 覆盖率检查失败！平均覆盖率 ${averageCoverage}% < ${THRESHOLD}%`);
        console.log('💡 请增加测试用例以提高覆盖率');
        process.exit(1);
    }
} catch (error) {
    console.error('❌ 解析覆盖率文件时出错:', error.message);
    process.exit(1);
}
