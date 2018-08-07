//
//  ViewController.swift
//  beacon-emulator
//
//  Created by Michael Vartanian on 8/7/18.
//  Copyright © 2018 Michael Vartanian. All rights reserved.
//

import UIKit
import CoreBluetooth
import CoreLocation

class ViewController: UIViewController, CBPeripheralManagerDelegate, UITextFieldDelegate {

    @IBOutlet weak var transmitStatusButton: UIButton!
    @IBOutlet weak var transmitBeaconUUIDTextField: UITextField!
    @IBOutlet weak var transmitBeaconMajorTextField: UITextField!
    @IBOutlet weak var transmitBeaconMinorTextField: UITextField!
    
    
    
    var localBeacon: CLBeaconRegion!
    var beaconPeripheralData: NSDictionary!
    var peripheralManager: CBPeripheralManager!
    
    var keyboardTagList = [1, 2]
    
    var gradientLayer: CAGradientLayer!
    var activeTextField = UITextField()
    
    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view, typically from a nib.
        
        transmitBeaconUUIDTextField.text = "8D847D20-0116-435F-9A21-2FA79A706D9E"
        transmitBeaconMajorTextField.text = String(8)
        transmitBeaconMinorTextField.text = String(2590)
        
        
        // Configure campaignBeaconUUIDTextField
        transmitBeaconUUIDTextField.delegate = self
        transmitBeaconUUIDTextField.tag = 0
        transmitBeaconUUIDTextField.returnKeyType = UIReturnKeyType.done
        
        // Configure campaignBeaconMajorTextField
        transmitBeaconMajorTextField.delegate = self
        transmitBeaconMajorTextField.tag = 1
        transmitBeaconMajorTextField.keyboardType = UIKeyboardType.numbersAndPunctuation
        transmitBeaconMajorTextField.returnKeyType = UIReturnKeyType.done
        
        // Configure campaignBeaconMinorTextField
        transmitBeaconMinorTextField.delegate = self
        transmitBeaconMinorTextField.tag = 2
        transmitBeaconMinorTextField.keyboardType = UIKeyboardType.numbersAndPunctuation
        transmitBeaconMinorTextField.returnKeyType = UIReturnKeyType.done
        
        // Adjust the keyboard/stack view height/location based on keyboard
        // Adopted from StackOverflow
        // https://stackoverflow.com/questions/26070242/move-view-with-keyboard-using-swift
        NotificationCenter.default.addObserver(self, selector: #selector(ViewController.keyboardWillShow), name: NSNotification.Name.UIKeyboardWillShow, object: nil)
        NotificationCenter.default.addObserver(self, selector: #selector(ViewController.keyboardWillHide), name: NSNotification.Name.UIKeyboardWillHide, object: nil)
        
    }

    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        gradientLayer = CAGradientLayer()
        createGradientLayer(inputViewController: self, gradientLayer: gradientLayer, startColor: UIColor.darkGray, endColor: UIColor.lightGray)
        
        //radarView.isHidden = true
    }

    @IBAction func toggleAdvertisingButton(_ sender: UIButton) {
        // Toggle the state of the button
        transmitStatusButton.isSelected = transmitStatusButton.isSelected ? false : true
        
        updateToggleButton(button: transmitStatusButton,
                           stateOneColor: UIColor.gray,
                           stateOneText: "Stop Advertising",
                           stateTwoColor: UIColor.blue,
                           stateTwoText: "Start Advertising")
        
        if transmitStatusButton.isSelected {
            if localBeacon != nil {
                stopLocalBeacon()
            }
            //radarView.isHidden = false
            
            let localBeaconUUID = transmitBeaconUUIDTextField.text
            let localBeaconMajor: CLBeaconMajorValue = CLBeaconMajorValue(transmitBeaconMajorTextField.text!)!
            let localBeaconMinor: CLBeaconMinorValue = CLBeaconMajorValue(transmitBeaconMinorTextField.text!)!
            let uuid = UUID(uuidString: localBeaconUUID!)!
            localBeacon = CLBeaconRegion(proximityUUID: uuid, major: localBeaconMajor, minor: localBeaconMinor, identifier: "Digital2Go Media Networks")
            
            beaconPeripheralData = localBeacon.peripheralData(withMeasuredPower: nil)
            peripheralManager = CBPeripheralManager(delegate: self, queue: nil, options: nil)
            //radarView.startAnimation()
        } else {
            stopLocalBeacon()
            //radarView.stopAnimation()
            //radarView.isHidden = true
        }
        
    }
    
    func stopLocalBeacon() {
        peripheralManager.stopAdvertising()
        peripheralManager = nil
        beaconPeripheralData = nil
        localBeacon = nil
    }
    
    func peripheralManagerDidUpdateState(_ peripheral: CBPeripheralManager) {
        if peripheral.state == .poweredOn {
            print("start advertising")
            peripheralManager.startAdvertising(beaconPeripheralData as! [String: AnyObject]!)
        } else if peripheral.state == .poweredOff {
            peripheralManager.stopAdvertising()
            print("stop advertising")
        }
    }
    
    // Adopted from StackOverflow to get 'Done' key and be able to return from textfield entries
    // http://stackoverflow.com/questions/31766896/switching-text-fields-on-pressing-return-key-in-swift
    // The first conditional not really needed as I am just exiting and not going to the next field but
    // keeping just in case I decide to use later.
    func textFieldShouldReturn(_ textField: UITextField) -> Bool {
        if let nextField = textField.superview?.viewWithTag(textField.tag + 1) as? UITextField {
            nextField.becomeFirstResponder()
        } else {
            textField.resignFirstResponder()
            return true
        }
        return false
    }
    
    // Adjust the keyboard/stack view height/location based on keyboard
    // Adopted from StackOverflow
    // https://stackoverflow.com/questions/26070242/move-view-with-keyboard-using-swift
    @objc func keyboardWillShow(notification: NSNotification) {
        for tag in keyboardTagList {
            // Only perform the shift if text field is part of tagged list
            if self.activeTextField.tag == tag {
                if let keyboardSize = (notification.userInfo?[UIKeyboardFrameBeginUserInfoKey] as? NSValue)?.cgRectValue {
                    if self.view.frame.origin.y == 0{
                        self.view.frame.origin.y -= keyboardSize.height
                    }
                }
            }
        }
    }
    
    // Adjust the keyboard/stack view height/location based on keyboard
    // Adopted from StackOverflow
    // https://stackoverflow.com/questions/26070242/move-view-with-keyboard-using-swift
    @objc func keyboardWillHide(notification: NSNotification) {
        for tag in keyboardTagList {
            // Only perform the shift if text field is part of tagged list
            if self.activeTextField.tag == tag {
                if let keyboardSize = (notification.userInfo?[UIKeyboardFrameBeginUserInfoKey] as? NSValue)?.cgRectValue {
                    if self.view.frame.origin.y != 0{
                        self.view.frame.origin.y += keyboardSize.height
                    }
                }
            }
        }
    }
    func textFieldDidBeginEditing(_ textField: UITextField) {
        self.activeTextField = textField
    }
}

